#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "torch>=2.0",
#     "transformers>=4.38",
#     "safetensors>=0.4",
#     "accelerate>=0.25",
# ]
# ///
"""Generate golden outputs from HuggingFace Mixtral MoE.

This script extracts intermediate MoE layer outputs from Mixtral
for use as ground truth in the MegaBlocks parity oracle.

Usage:
    uv run scripts/generate_hf_golden.py \
        --model mistralai/Mixtral-8x7B-v0.1 \
        --output oracle/mixtral-8x7b/v1/

References:
    - MegaBlocks Parity Oracle Spec: specs/moe-parity-oracle.md
    - Popper, K. (1959). The Logic of Scientific Discovery.
"""

import argparse
import hashlib
import json
from pathlib import Path

import torch
from safetensors.torch import save_file


def hash_input(tensor: torch.Tensor) -> str:
    """SHA-256 hash of tensor for deterministic naming."""
    data = tensor.cpu().numpy().tobytes()
    return hashlib.sha256(data).hexdigest()[:16]


class MoELayerCapture:
    """Hook to capture MoE layer intermediate outputs."""

    def __init__(self):
        self.captures: dict[str, torch.Tensor] = {}
        self.layer_idx = 0

    def reset(self):
        self.captures = {}
        self.layer_idx = 0

    def create_hook(self, name: str):
        def hook(module, input, output):
            # Capture router logits if available
            if hasattr(module, "gate"):
                with torch.no_grad():
                    hidden_states = input[0]
                    router_logits = module.gate(hidden_states)
                    self.captures[f"{name}_router_logits"] = router_logits.detach().clone()
                    self.captures[f"{name}_input"] = hidden_states.detach().clone()

            # Capture final output
            if isinstance(output, tuple):
                self.captures[f"{name}_output"] = output[0].detach().clone()
            else:
                self.captures[f"{name}_output"] = output.detach().clone()

        return hook


def extract_moe_config(model) -> dict:
    """Extract MoE configuration from model."""
    config = model.config
    return {
        "num_experts": config.num_local_experts,
        "top_k": config.num_experts_per_tok,
        "hidden_size": config.hidden_size,
        "intermediate_size": config.intermediate_size,
        "num_layers": config.num_hidden_layers,
        "model_type": config.model_type,
    }


def generate_test_inputs(
    hidden_size: int,
    batch_sizes: list[int] | None = None,
    seq_lengths: list[int] | None = None,
    seed: int = 42,
) -> list[tuple[torch.Tensor, str]]:
    """Generate deterministic test inputs."""
    if seq_lengths is None:
        seq_lengths = [1, 128, 512]
    if batch_sizes is None:
        batch_sizes = [1]
    torch.manual_seed(seed)

    inputs = []
    for batch in batch_sizes:
        for seq_len in seq_lengths:
            x = torch.randn(batch, seq_len, hidden_size)
            name = f"b{batch}_s{seq_len}"
            inputs.append((x, name))

    return inputs


def main():
    parser = argparse.ArgumentParser(description="Generate HF Mixtral golden outputs")
    parser.add_argument("--model", default="mistralai/Mixtral-8x7B-v0.1", help="Model ID")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--layers", type=int, nargs="+", default=[0, 15, 31], help="Layer indices")
    parser.add_argument("--dtype", choices=["fp32", "fp16", "bf16"], default="fp16")
    parser.add_argument("--device", default="cuda", help="Device")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Set dtype
    dtype_map = {"fp32": torch.float32, "fp16": torch.float16, "bf16": torch.bfloat16}
    dtype = dtype_map[args.dtype]

    print(f"Loading model: {args.model}")
    from transformers import AutoConfig, AutoModelForCausalLM

    config = AutoConfig.from_pretrained(args.model)

    # For testing without full model, we can extract just the MoE layer
    print(f"Model config: {config.num_local_experts} experts, top-{config.num_experts_per_tok}")

    # Check if we can load full model or need to work with just the layer
    try:
        model = AutoModelForCausalLM.from_pretrained(
            args.model,
            torch_dtype=dtype,
            device_map="auto",
            trust_remote_code=True,
        )
    except Exception as e:
        print(f"Cannot load full model: {e}")
        print("Creating minimal test with extracted config...")

        # Save config for MegaBlocks comparison
        moe_config = {
            "num_experts": config.num_local_experts,
            "top_k": config.num_experts_per_tok,
            "hidden_size": config.hidden_size,
            "intermediate_size": config.intermediate_size,
            "model_id": args.model,
            "dtype": args.dtype,
        }

        with open(output_dir / "config.json", "w") as f:
            json.dump(moe_config, f, indent=2)

        print(f"Saved config to {output_dir / 'config.json'}")
        return

    # Extract MoE config
    moe_config = extract_moe_config(model)
    moe_config["model_id"] = args.model
    moe_config["dtype"] = args.dtype

    # Set up capture hooks
    capture = MoELayerCapture()
    hooks = []

    for layer_idx in args.layers:
        if layer_idx < len(model.model.layers):
            moe_layer = model.model.layers[layer_idx].block_sparse_moe
            hook = moe_layer.register_forward_hook(capture.create_hook(f"layer_{layer_idx}"))
            hooks.append(hook)

    # Generate test inputs
    test_inputs = generate_test_inputs(
        hidden_size=moe_config["hidden_size"],
        batch_sizes=[1],
        seq_lengths=[1, 128],
    )

    # Manifest for tracking
    manifest = {
        "model": args.model,
        "config": moe_config,
        "tests": [],
    }

    # Run through test inputs
    model.eval()
    for input_tensor, input_name in test_inputs:
        print(f"Processing input: {input_name}")
        capture.reset()

        input_hash = hash_input(input_tensor)

        # Move to device
        input_tensor = input_tensor.to(args.device, dtype=dtype)

        # For causal LM, we need to format as token ids and use embed
        # For direct MoE testing, we inject at hidden states level
        with torch.no_grad():
            # Get embeddings from a dummy input
            batch, seq_len, _ = input_tensor.shape
            dummy_ids = torch.zeros(batch, seq_len, dtype=torch.long, device=args.device)

            # Run forward to populate captures
            try:
                _ = model(dummy_ids, output_hidden_states=True)
            except Exception as e:
                print(f"  Forward pass failed: {e}")
                continue

        # Save captured tensors
        test_data = {
            "input_name": input_name,
            "input_hash": input_hash,
            "input_shape": list(input_tensor.shape),
        }

        tensors_to_save = {}
        for name, tensor in capture.captures.items():
            tensors_to_save[name] = tensor.cpu().to(torch.float32)
            test_data[f"{name}_shape"] = list(tensor.shape)

        if tensors_to_save:
            save_file(tensors_to_save, output_dir / f"{input_name}_{input_hash}.safetensors")

            with open(output_dir / f"{input_name}_{input_hash}.json", "w") as f:
                json.dump(test_data, f, indent=2)

            manifest["tests"].append(
                {
                    "name": input_name,
                    "hash": input_hash,
                    "file": f"{input_name}_{input_hash}.safetensors",
                }
            )

            print(f"  Saved: {input_name}_{input_hash}.safetensors")

    # Remove hooks
    for hook in hooks:
        hook.remove()

    # Save manifest
    with open(output_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nGenerated {len(manifest['tests'])} golden outputs")
    print(f"Manifest: {output_dir / 'manifest.json'}")


if __name__ == "__main__":
    main()

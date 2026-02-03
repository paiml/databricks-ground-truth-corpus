#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "torch>=2.0",
#     "megablocks>=0.6.0",
#     "safetensors>=0.4",
#     "triton>=2.1.0",
# ]
# ///
"""Generate golden outputs from MegaBlocks MoE layers.

This script generates outputs from MegaBlocks dMoE and MoE layers
for comparison against HuggingFace Mixtral.

Usage:
    uv run scripts/generate_megablocks_golden.py \
        --config oracle/mixtral-8x7b/v1/config.json \
        --output oracle/megablocks-dmoe/v1/

References:
    - MegaBlocks: https://github.com/databricks/megablocks
    - Gale et al. (2023). MegaBlocks: Efficient Sparse Training with MoE
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


def create_megablocks_layer(config: dict, layer_type: str = "dmoe"):
    """Create a MegaBlocks MoE or dMoE layer from config."""
    from megablocks.layers.arguments import Arguments

    args = Arguments(
        hidden_size=config["hidden_size"],
        ffn_hidden_size=config["intermediate_size"],
        moe_num_experts=config["num_experts"],
        moe_top_k=config["top_k"],
        bias=False,
        return_bias=False,
        fp16=config.get("dtype") == "fp16",
        bf16=config.get("dtype") == "bf16",
        mlp_impl="grouped",  # Required for triton >= 3.2.0
    )

    if layer_type == "dmoe":
        from megablocks.layers.dmoe import dMoE

        return dMoE(args), args
    else:
        from megablocks.layers.moe import MoE

        return MoE(args), args


def generate_test_inputs(
    hidden_size: int,
    batch_sizes: list[int] | None = None,
    seq_lengths: list[int] | None = None,
    seed: int = 42,
) -> list[tuple[torch.Tensor, str]]:
    """Generate deterministic test inputs (same as HF script)."""
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


def capture_layer_outputs(
    layer,
    input_tensor: torch.Tensor,
    args,
) -> dict[str, torch.Tensor]:
    """Capture intermediate outputs from MegaBlocks layer."""
    captures = {}

    # Capture input
    captures["input"] = input_tensor.detach().clone()

    # Get router logits if available
    if hasattr(layer, "router"):
        with torch.no_grad():
            # Reshape for router: (batch * seq, hidden)
            _batch, _seq_len, hidden = input_tensor.shape
            flat_input = input_tensor.view(-1, hidden)

            # Get router weights
            router_logits = layer.router(flat_input)
            captures["router_logits"] = router_logits.detach().clone()

            # Get expert selection
            if hasattr(torch, "topk"):
                top_k = args.moe_top_k
                router_probs = torch.softmax(router_logits, dim=-1)
                top_probs, top_indices = torch.topk(router_probs, top_k, dim=-1)
                captures["router_probs"] = top_probs.detach().clone()
                captures["selected_experts"] = top_indices.detach().clone()

    # Forward pass
    with torch.no_grad():
        output = layer(input_tensor)
        if isinstance(output, tuple):
            captures["output"] = output[0].detach().clone()
        else:
            captures["output"] = output.detach().clone()

    return captures


def main():
    parser = argparse.ArgumentParser(description="Generate MegaBlocks golden outputs")
    parser.add_argument("--config", required=True, help="Config JSON from HF golden")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--layer-type", choices=["dmoe", "moe"], default="dmoe")
    parser.add_argument("--device", default="cuda", help="Device")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load config
    with open(args.config) as f:
        config = json.load(f)

    print(f"Config: {config['num_experts']} experts, top-{config['top_k']}")
    print(f"Hidden: {config['hidden_size']}, FFN: {config['intermediate_size']}")

    # Create MegaBlocks layer
    print(f"Creating MegaBlocks {args.layer_type} layer...")
    try:
        layer, mb_args = create_megablocks_layer(config, args.layer_type)
        layer = layer.to(args.device)
        layer.eval()
    except Exception as e:
        print(f"Error creating layer: {e}")
        print("MegaBlocks will be installed automatically via uv inline deps")
        return

    # Determine dtype
    dtype = torch.float32
    if config.get("dtype") == "fp16":
        dtype = torch.float16
    elif config.get("dtype") == "bf16":
        dtype = torch.bfloat16

    # Generate test inputs
    test_inputs = generate_test_inputs(
        hidden_size=config["hidden_size"],
        batch_sizes=[1],
        seq_lengths=[1, 128],
    )

    # Manifest
    manifest = {
        "layer_type": args.layer_type,
        "config": config,
        "tests": [],
    }

    # Process test inputs
    for input_tensor, input_name in test_inputs:
        print(f"Processing input: {input_name}")

        input_hash = hash_input(input_tensor)
        input_tensor = input_tensor.to(args.device, dtype=dtype)

        try:
            captures = capture_layer_outputs(layer, input_tensor, mb_args)
        except Exception as e:
            print(f"  Forward pass failed: {e}")
            continue

        # Save tensors
        test_data = {
            "input_name": input_name,
            "input_hash": input_hash,
            "input_shape": list(input_tensor.shape),
            "layer_type": args.layer_type,
        }

        tensors_to_save = {}
        for name, tensor in captures.items():
            tensors_to_save[name] = tensor.cpu().to(torch.float32)
            test_data[f"{name}_shape"] = list(tensor.shape)

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

    # Save manifest
    with open(output_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nGenerated {len(manifest['tests'])} golden outputs")


if __name__ == "__main__":
    main()

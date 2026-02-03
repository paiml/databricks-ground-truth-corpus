# MegaBlocks MoE

Ground truth tests for MegaBlocks Mixture-of-Experts (MoE) implementation parity with HuggingFace Mixtral.

## Test Coverage: 8/30 (27%)

Most tests require GPU infrastructure and grouped_gemm library.

## Overview

[MegaBlocks](https://github.com/databricks/megablocks) provides efficient sparse MoE training. Tests validate numerical parity with HuggingFace's Mixtral implementation.

## MoE Architecture

```
Input Tokens
     │
     ▼
┌─────────┐
│ Router  │  ← Gating network selects top-k experts
└────┬────┘
     │ top-k indices + weights
     ▼
┌─────────────────────────────────┐
│  Expert 0  │  Expert 1  │ ...  │  ← Parallel expert forward
└─────────────────────────────────┘
     │
     ▼
┌─────────────┐
│ Combine     │  ← Weighted sum of expert outputs
└─────────────┘
     │
     ▼
Output
```

## Test Categories

### Router Tests (4/10)

| Test | Description | Status |
|------|-------------|--------|
| MOE-001 | Top-k selection correctness | Pass |
| MOE-002 | Router weight normalization | Pass |
| MOE-003 | Load balancing auxiliary loss | Pass |
| MOE-004 | Expert capacity enforcement | Pass |
| MOE-005 | Gradient flow through router | Skip (GPU) |
| ... | | |

### Expert Forward Tests (2/10)

| Test | Description | Status |
|------|-------------|--------|
| MOE-011 | Single expert forward | Pass |
| MOE-012 | Multi-expert parallel forward | Pass |
| MOE-013 | Expert output shapes | Skip (GPU) |
| ... | | |

### Numerical Parity Tests (2/10)

| Test | Description | Status |
|------|-------------|--------|
| MOE-021 | HuggingFace Mixtral parity | Pass |
| MOE-022 | fp32 tolerance compliance | Pass |
| MOE-023 | fp16 inference parity | Skip (GPU) |
| ... | | |

## Ground Truth Validation

```python
def test_moe_huggingface_parity():
    """MegaBlocks output must match HuggingFace within tolerance."""
    # Reference: HuggingFace Mixtral 8x7B
    input_ids = torch.tensor([[1, 2, 3, 4, 5]])

    # HuggingFace reference
    hf_model = AutoModelForCausalLM.from_pretrained("mistralai/Mixtral-8x7B-v0.1")
    hf_output = hf_model(input_ids).logits

    # MegaBlocks implementation
    mb_model = load_megablocks_model("mixtral-8x7b")
    mb_output = mb_model(input_ids).logits

    # Validate parity
    torch.testing.assert_close(
        mb_output,
        hf_output,
        atol=1e-5,  # fp32 tolerance
        rtol=1e-4,
    )
```

## Tolerance Standards

| Precision | Absolute | Relative | Use Case |
|-----------|----------|----------|----------|
| fp32 | 1e-5 | 1e-4 | Training |
| fp16 | 1e-3 | 1e-2 | Inference |
| int8 | 1e-1 | N/A | Quantized |

## Running Tests

```bash
# Run available tests (no GPU required)
uv run megablocks/scripts/test_moe_parity.py

# Full tests (requires GPU + grouped_gemm)
uv run megablocks/scripts/test_moe_parity.py --full
```

## Infrastructure Requirements

Full test suite requires:
- NVIDIA GPU with CUDA 11.8+
- `grouped_gemm` library
- `megablocks` package
- HuggingFace `transformers`
- ~50GB GPU memory for Mixtral 8x7B

## References

- [MegaBlocks Paper](https://arxiv.org/abs/2211.15841)
- [Mixtral Technical Report](https://arxiv.org/abs/2401.04088)
- [HuggingFace Mixtral](https://huggingface.co/mistralai/Mixtral-8x7B-v0.1)

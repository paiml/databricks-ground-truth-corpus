# MegaBlocks MoE Parity Oracle

**Version:** 1.0.0
**Date:** 2026-02-03
**Methodology:** Popperian Falsification
**Reference:** Gale et al. (2023) "MegaBlocks: Efficient Sparse Training with MoE"

---

## 1. Overview

MegaBlocks provides efficient Mixture-of-Experts (MoE) and dropless-MoE (dMoE) layers. This oracle validates numerical parity against reference implementations.

### Reference Implementations

| Implementation | Purpose | Repository |
|---------------|---------|------------|
| HuggingFace Mixtral | MoE reference | transformers |
| MegaBlocks dMoE | Under test | databricks/megablocks |
| MegaBlocks MoE | Under test | databricks/megablocks |
| Tutel MoE | Baseline | microsoft/tutel |

---

## 2. Layer Architecture

### 2.1 MoE Layer Components

```
Input (batch, seq, hidden)
    │
    ▼
┌─────────────┐
│   Router    │ ─── Expert selection (top-k)
└─────────────┘
    │
    ▼
┌─────────────┐
│   Experts   │ ─── N parallel FFN experts
│  (sparse)   │
└─────────────┘
    │
    ▼
┌─────────────┐
│  Combine    │ ─── Weighted sum by router scores
└─────────────┘
    │
    ▼
Output (batch, seq, hidden)
```

### 2.2 dMoE Innovation

- **No token dropping**: All tokens processed
- **Block-sparse operations**: Efficient GPU utilization
- **No capacity_factor**: Simplified hyperparameter space

---

## 3. Parity Test Categories

### 3.1 Router Parity

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| RT-001 | Router logits computation | Identical to HF | fp32: 1e-5 |
| RT-002 | Top-k expert selection | Same expert indices | Exact |
| RT-003 | Router probability normalization | Sum to 1.0 | 1e-6 |
| RT-004 | Load balancing auxiliary loss | Same loss value | fp32: 1e-5 |
| RT-005 | Expert assignment determinism | Reproducible | Exact |

### 3.2 Expert FFN Parity

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| EX-001 | Expert weight shapes | Match config | Exact |
| EX-002 | SwiGLU activation | Same output | fp32: 1e-5 |
| EX-003 | Expert bias (if present) | Same output | fp32: 1e-5 |
| EX-004 | Hidden dimension mapping | d_model → d_ff → d_model | Exact |
| EX-005 | Per-expert computation | Isolated correctness | fp32: 1e-5 |

### 3.3 Block-Sparse Operations (dMoE)

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| BS-001 | Block size alignment | Power of 2 | Exact |
| BS-002 | Sparse matrix construction | Same sparsity pattern | Exact |
| BS-003 | Block-sparse matmul | Numerically equivalent | fp32: 1e-4 |
| BS-004 | Memory layout | Row-major blocks | Exact |
| BS-005 | Padding handling | Correct masking | Exact |

### 3.4 Output Combination

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| OC-001 | Expert output weighting | router_prob * expert_out | fp32: 1e-5 |
| OC-002 | Multi-expert combination | Sum over k experts | fp32: 1e-5 |
| OC-003 | Residual connection | output + input | fp32: 1e-5 |
| OC-004 | Output normalization | If RMSNorm present | fp32: 1e-5 |

### 3.5 Training Parity

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| TR-001 | Gradient w.r.t. router | Same gradient | fp32: 1e-4 |
| TR-002 | Gradient w.r.t. experts | Same gradient | fp32: 1e-4 |
| TR-003 | Auxiliary loss gradient | Correct backprop | fp32: 1e-4 |
| TR-004 | Expert parallelism gradients | All-reduce correct | fp32: 1e-4 |
| TR-005 | Mixed precision (fp16/bf16) | Numerically stable | fp16: 1e-3 |

---

## 4. Golden Corpus Structure

```
megablocks/
├── oracle/
│   ├── mixtral-8x7b/          # HuggingFace reference
│   │   ├── v1/
│   │   │   ├── manifest.json
│   │   │   ├── router_test_001.safetensors
│   │   │   ├── router_test_001.json
│   │   │   └── ...
│   │   └── prompts.txt
│   ├── megablocks-moe/        # MegaBlocks MoE outputs
│   │   └── v1/
│   └── megablocks-dmoe/       # MegaBlocks dMoE outputs
│       └── v1/
├── specs/
│   └── moe-parity-oracle.md
└── scripts/
    ├── generate_hf_golden.py
    ├── generate_megablocks_golden.py
    └── validate_parity.py
```

### Golden Output Format

```json
{
  "test_id": "RT-001",
  "layer": "moe_layer_0",
  "input_hash": "abc123...",
  "input_shape": [1, 128, 4096],
  "config": {
    "num_experts": 8,
    "top_k": 2,
    "hidden_dim": 4096,
    "intermediate_dim": 14336
  },
  "outputs": {
    "router_logits_shape": [1, 128, 8],
    "selected_experts": [[0, 3], [1, 5], ...],
    "router_probs": [0.52, 0.48, ...],
    "expert_outputs_hash": "def456..."
  }
}
```

### Tensor Storage (SafeTensors)

```python
{
    "input": tensor([1, 128, 4096], dtype=float32),
    "router_logits": tensor([1, 128, 8], dtype=float32),
    "expert_outputs": tensor([1, 128, 4096], dtype=float32),
    "final_output": tensor([1, 128, 4096], dtype=float32)
}
```

---

## 5. Test Configurations

### 5.1 Model Configurations

| Config | Experts | Top-K | Hidden | Intermediate |
|--------|---------|-------|--------|--------------|
| small | 4 | 1 | 512 | 2048 |
| medium | 8 | 2 | 2048 | 8192 |
| mixtral | 8 | 2 | 4096 | 14336 |
| large | 16 | 2 | 4096 | 14336 |

### 5.2 Input Configurations

| Config | Batch | Sequence | Purpose |
|--------|-------|----------|---------|
| single | 1 | 1 | Minimal test |
| short | 1 | 128 | Standard |
| long | 1 | 2048 | Long context |
| batched | 4 | 512 | Batch effects |

---

## 6. Execution

### 6.1 Prerequisites

**CRITICAL: All Python dependencies use uv inline script metadata (PEP 723)**

```bash
# Run any script directly with uv - dependencies install automatically:
uv run scripts/test_moe_properties.py
uv run scripts/generate_hf_golden.py --help
uv run scripts/validate_parity.py --help

# For full MegaBlocks dMoE testing with triton >= 3.2.0:
# grouped_gemm must be installed from source (requires CUDA build):
uv pip install git+https://github.com/tgale96/grouped_gemm@main
```

**Dependency Matrix:**

| Component | Package | Notes |
|-----------|---------|-------|
| Reference tests | torch, numpy | Standard PyPI |
| HuggingFace golden | transformers, safetensors | Standard PyPI |
| MegaBlocks MoE | megablocks, triton | Standard PyPI |
| MegaBlocks dMoE | grouped_gemm | Build from source |

### 6.2 Generate HuggingFace Golden Outputs

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["torch>=2.0", "transformers>=4.38", "safetensors>=0.4"]
# ///

from transformers import AutoModelForCausalLM
import torch
from safetensors.torch import save_file

model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mixtral-8x7B-v0.1",
    torch_dtype=torch.float32,
    device_map="auto"
)

# Extract MoE layer
moe_layer = model.model.layers[0].block_sparse_moe

# Generate golden outputs for test inputs
input_tensor = torch.randn(1, 128, 4096)
with torch.no_grad():
    router_logits = moe_layer.gate(input_tensor)
    # ... capture intermediate outputs
```

### 6.2 Generate MegaBlocks Golden Outputs

```python
from megablocks.layers import dmoe, moe
import torch

layer = dmoe.dMoE(
    hidden_size=4096,
    ffn_hidden_size=14336,
    num_experts=8,
    top_k=2
)

# Same input tensor
input_tensor = torch.randn(1, 128, 4096)
output = layer(input_tensor)
```

### 6.3 Parity Validation

```bash
# Compare HuggingFace vs MegaBlocks
python scripts/validate_parity.py \
    --reference oracle/mixtral-8x7b/v1 \
    --candidate oracle/megablocks-dmoe/v1 \
    --tolerance fp32
```

---

## 7. Falsification Checklist

### 7.1 Router Tests
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| RT-001 | Router logits match HF | atol=1e-5 | | |
| RT-002 | Same experts selected | Exact match | | |
| RT-003 | Probabilities sum to 1 | Within 1e-6 | | |
| RT-004 | Load balance loss | atol=1e-5 | | |
| RT-005 | Deterministic selection | Reproducible | | |

### 7.2 Expert FFN Tests
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| EX-001 | Weight shapes | Match config | | |
| EX-002 | SwiGLU output | atol=1e-5 | | |
| EX-003 | Bias term | atol=1e-5 | | |
| EX-004 | Dimension mapping | Correct | | |
| EX-005 | Per-expert output | atol=1e-5 | | |

### 7.3 Block-Sparse Tests
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| BS-001 | Block alignment | Power of 2 | | |
| BS-002 | Sparsity pattern | Matches | | |
| BS-003 | Sparse matmul | atol=1e-4 | | |
| BS-004 | Memory layout | Row-major | | |
| BS-005 | Padding | Correct | | |

### 7.4 Output Tests
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| OC-001 | Expert weighting | atol=1e-5 | | |
| OC-002 | Multi-expert sum | atol=1e-5 | | |
| OC-003 | Residual | atol=1e-5 | | |
| OC-004 | Normalization | atol=1e-5 | | |

### 7.5 Training Tests
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| TR-001 | Router gradient | atol=1e-4 | | |
| TR-002 | Expert gradient | atol=1e-4 | | |
| TR-003 | Aux loss gradient | atol=1e-4 | | |
| TR-004 | Expert parallel | Correct | | |
| TR-005 | Mixed precision | Stable | | |

---

## 8. Performance Comparison

Beyond correctness, track performance claims:

| Metric | MegaBlocks | Tutel | Expected Delta |
|--------|------------|-------|----------------|
| Throughput (tokens/s) | X | Y | +40% |
| Memory (GB) | X | Y | Similar |
| Training time | X | Y | 2.4x faster |

---

## References

- Gale, T. et al. (2023). MegaBlocks: Efficient Sparse Training with MoE
- Fedus, W. et al. (2022). Switch Transformers
- Jiang, A. et al. (2024). Mixtral of Experts
- Goldberg, D. (1991). What Every Computer Scientist Should Know About FP

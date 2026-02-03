# Cross-Implementation Testing

Cross-implementation testing validates behavior consistency across different implementations of the same specification.

## Why Cross-Implementation?

Single-implementation tests can only verify internal consistency. Cross-implementation tests verify:

1. **Specification compliance**: Does the implementation match the spec?
2. **Interoperability**: Do different implementations produce compatible outputs?
3. **Edge case handling**: Do implementations agree on undefined behaviors?

## Example: SDK Parity

The Databricks SDK exists in Python, Go, and Java. All must produce consistent API calls:

```python
# Python SDK
client.jobs.create(
    name="my-job",
    max_concurrent_runs=5,
    timeout_seconds=3600,
)

# Go SDK
client.Jobs.Create(ctx, jobs.CreateJob{
    Name:              "my-job",
    MaxConcurrentRuns: 5,
    TimeoutSeconds:    3600,
})

# Java SDK
client.jobs().create(new CreateJob()
    .setName("my-job")
    .setMaxConcurrentRuns(5)
    .setTimeoutSeconds(3600L));
```

### Ground Truth Validation

```python
def test_sdk_type_mappings():
    """SDK types must map consistently across languages."""
    GROUND_TRUTH = {
        "python_int": ("go_int64", "java_Long"),
        "python_str": ("go_string", "java_String"),
        "python_bool": ("go_bool", "java_Boolean"),
        "python_list": ("go_slice", "java_List"),
        "python_dict": ("go_map", "java_Map"),
        "python_datetime": ("go_time.Time", "java_Instant"),
    }

    for py_type, (go_type, java_type) in GROUND_TRUTH.items():
        # Verify mappings exist and are bidirectional
        assert map_py_to_go(py_type) == go_type
        assert map_py_to_java(py_type) == java_type
```

## Example: SQL Connectors

SQL results must be identical across connector languages:

```python
GROUND_TRUTH_QUERY = """
SELECT
    CAST(1 AS INT) as int_col,
    CAST(1.5 AS DOUBLE) as double_col,
    'hello' as string_col,
    CAST('2024-01-15' AS DATE) as date_col
"""

EXPECTED_RESULT = {
    "int_col": 1,
    "double_col": 1.5,
    "string_col": "hello",
    "date_col": "2024-01-15",
}

def test_python_connector():
    result = python_connector.execute(GROUND_TRUTH_QUERY)
    assert result == EXPECTED_RESULT

def test_go_connector():
    result = go_connector.execute(GROUND_TRUTH_QUERY)
    assert result == EXPECTED_RESULT

def test_nodejs_connector():
    result = nodejs_connector.execute(GROUND_TRUTH_QUERY)
    assert result == EXPECTED_RESULT
```

## Example: ML Model Parity

MegaBlocks MoE outputs must match HuggingFace reference:

```python
def test_moe_output_parity():
    """MegaBlocks must match HuggingFace Mixtral within fp32 tolerance."""
    input_tokens = [1, 2, 3, 4, 5]

    # Reference implementation
    hf_output = huggingface_mixtral(input_tokens)

    # Implementation under test
    mb_output = megablocks_moe(input_tokens)

    # Cross-implementation validation
    np.testing.assert_allclose(
        mb_output,
        hf_output,
        atol=1e-5,
        rtol=1e-4,
    )
```

## Capturing Golden Outputs

For implementations requiring external infrastructure:

```python
# Step 1: Capture golden outputs (requires Databricks workspace)
def capture_golden_outputs():
    """Run once to capture reference outputs."""
    results = {}
    for query in TEST_QUERIES:
        results[query] = databricks_connector.execute(query)

    with open("oracle/golden_outputs.json", "w") as f:
        json.dump(results, f)

# Step 2: Validate against golden outputs (no infrastructure needed)
def test_against_golden():
    """Validate local implementation against captured outputs."""
    with open("oracle/golden_outputs.json") as f:
        golden = json.load(f)

    for query, expected in golden.items():
        actual = local_implementation(query)
        assert actual == expected
```

## Cross-Implementation Matrix

| Domain | Implementation A | Implementation B | Comparison |
|--------|-----------------|-----------------|------------|
| SDK | Python | Go, Java | Request/response JSON |
| SQL | Python connector | Go, Node, JDBC | Query results |
| MegaBlocks | MegaBlocks | HuggingFace | Tensor outputs |
| pandas API | Koalas | pandas | DataFrame operations |
| TPC | Our queries | TPC spec | Row counts, checksums |

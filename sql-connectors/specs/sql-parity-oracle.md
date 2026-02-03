# SQL Connectors Cross-Language Parity Oracle

**Version:** 1.0.0
**Date:** 2026-02-03
**Methodology:** Popperian Falsification

---

## 1. Overview

Databricks provides SQL connectors in multiple languages. This oracle validates that identical queries produce identical results across all connectors.

### Connectors Under Test

| Connector | Language | Repository | Stars |
|-----------|----------|------------|-------|
| databricks-sql-python | Python | databricks/databricks-sql-python | 220 |
| databricks-sql-go | Go | databricks/databricks-sql-go | 44 |
| databricks-sql-nodejs | TypeScript | databricks/databricks-sql-nodejs | 31 |
| databricks-jdbc | Java | databricks/databricks-jdbc | 30 |
| databricks-sqlalchemy | Python | databricks/databricks-sqlalchemy | 19 |

---

## 2. Parity Categories

### 2.1 Data Type Mapping

| SQL Type | Python | Go | Java | Node.js | Tolerance |
|----------|--------|-----|------|---------|-----------|
| BOOLEAN | bool | bool | Boolean | boolean | Exact |
| TINYINT | int | int8 | Byte | number | Exact |
| SMALLINT | int | int16 | Short | number | Exact |
| INT | int | int32 | Integer | number | Exact |
| BIGINT | int | int64 | Long | bigint | Exact |
| FLOAT | float | float32 | Float | number | 1e-6 |
| DOUBLE | float | float64 | Double | number | 1e-15 |
| DECIMAL(p,s) | Decimal | decimal.Decimal | BigDecimal | string | Exact |
| STRING | str | string | String | string | Exact |
| BINARY | bytes | []byte | byte[] | Buffer | Exact |
| DATE | date | time.Time | LocalDate | Date | Exact |
| TIMESTAMP | datetime | time.Time | Instant | Date | 1ms |
| TIMESTAMP_NTZ | datetime | time.Time | LocalDateTime | Date | 1ms |
| ARRAY<T> | list | []T | List<T> | Array | Recursive |
| MAP<K,V> | dict | map[K]V | Map<K,V> | Object | Recursive |
| STRUCT | dict/namedtuple | struct | Object | Object | Recursive |

### 2.2 Query Execution Parity

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| QE-001 | Simple SELECT | Same rows | Exact |
| QE-002 | SELECT with WHERE | Same filtered rows | Exact |
| QE-003 | JOIN results | Same joined rows | Exact |
| QE-004 | GROUP BY aggregates | Same aggregates | Numeric |
| QE-005 | ORDER BY | Same order | Exact |
| QE-006 | LIMIT/OFFSET | Same subset | Exact |
| QE-007 | UNION/INTERSECT/EXCEPT | Same set operation | Exact |
| QE-008 | Subqueries | Same results | Exact |
| QE-009 | Window functions | Same windows | Numeric |
| QE-010 | CTEs | Same CTE results | Exact |

### 2.3 NULL Handling

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| NL-001 | NULL in column | Language null type | Exact |
| NL-002 | NULL in aggregate | Correct handling | Exact |
| NL-003 | NULL comparison | Three-valued logic | Exact |
| NL-004 | COALESCE/IFNULL | Same substitution | Exact |
| NL-005 | NULL in array | Element vs array null | Exact |

### 2.4 Error Handling

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| ER-001 | Syntax error | Same error code | Exact |
| ER-002 | Table not found | Same error type | Semantic |
| ER-003 | Column not found | Same error type | Semantic |
| ER-004 | Type mismatch | Same error type | Semantic |
| ER-005 | Permission denied | Same error type | Semantic |
| ER-006 | Query timeout | Same behavior | Configurable |

### 2.5 Connection Management

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| CM-001 | Connection pooling | Same behavior | Configurable |
| CM-002 | Reconnection | Same retry logic | Configurable |
| CM-003 | Statement timeout | Same enforcement | 1s |
| CM-004 | Cursor management | Same lifecycle | Documented |
| CM-005 | Transaction isolation | Same level | Exact |

### 2.6 Parameterized Queries

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| PQ-001 | String parameters | Same escaping | Exact |
| PQ-002 | Numeric parameters | Same binding | Exact |
| PQ-003 | Date/time parameters | Same conversion | 1ms |
| PQ-004 | Array parameters | Same serialization | Exact |
| PQ-005 | NULL parameters | Same handling | Exact |
| PQ-006 | Named parameters | Same binding | Exact |

---

## 3. Golden Corpus Structure

```
sql-connectors/
├── oracle/
│   ├── queries/
│   │   ├── basic/
│   │   │   ├── select_all.sql
│   │   │   ├── select_where.sql
│   │   │   └── ...
│   │   ├── types/
│   │   │   ├── numeric_types.sql
│   │   │   ├── string_types.sql
│   │   │   ├── datetime_types.sql
│   │   │   └── complex_types.sql
│   │   ├── aggregates/
│   │   ├── joins/
│   │   └── edge_cases/
│   ├── expected/
│   │   ├── select_all.json
│   │   ├── select_where.json
│   │   └── ...
│   └── manifest.json
├── specs/
│   └── sql-parity-oracle.md
└── scripts/
    ├── capture_golden.py
    ├── validate_python.py
    ├── validate_go.go
    ├── validate_java.java
    └── validate_nodejs.ts
```

### Query Format

```sql
-- File: queries/types/decimal_precision.sql
-- ID: DT-DECIMAL-001
-- Description: Verify DECIMAL precision preservation
SELECT
    CAST(123.456789012345678901234567890 AS DECIMAL(38, 30)) as high_precision,
    CAST(0.1 + 0.2 AS DECIMAL(10, 2)) as float_artifact
```

### Expected Result Format

```json
{
  "query_id": "DT-DECIMAL-001",
  "query_file": "types/decimal_precision.sql",
  "columns": [
    {"name": "high_precision", "type": "DECIMAL(38,30)"},
    {"name": "float_artifact", "type": "DECIMAL(10,2)"}
  ],
  "rows": [
    {
      "high_precision": "123.456789012345678901234567890",
      "float_artifact": "0.30"
    }
  ],
  "expected_by_language": {
    "python": {"high_precision": "Decimal('123.456789012345678901234567890')"},
    "go": {"high_precision": "decimal.NewFromString(\"123.456789012345678901234567890\")"},
    "java": {"high_precision": "new BigDecimal(\"123.456789012345678901234567890\")"},
    "nodejs": {"high_precision": "\"123.456789012345678901234567890\""}
  }
}
```

---

## 4. Type-Specific Tests

### 4.1 Numeric Types

```sql
-- INT boundaries
SELECT
    2147483647 as max_int,
    -2147483648 as min_int,
    9223372036854775807 as max_bigint;

-- Float precision
SELECT
    CAST(1.7976931348623157E308 AS DOUBLE) as max_double,
    CAST(2.2250738585072014E-308 AS DOUBLE) as min_double,
    CAST('NaN' AS DOUBLE) as nan_value,
    CAST('Infinity' AS DOUBLE) as inf_value;

-- Decimal edge cases
SELECT
    CAST(99999999999999999999999999999999999999 AS DECIMAL(38,0)) as max_decimal,
    CAST(0.00000000000000000000000000000000000001 AS DECIMAL(38,38)) as min_decimal;
```

### 4.2 Timestamp Types

```sql
-- Timezone handling
SELECT
    TIMESTAMP '2024-01-15 12:30:45.123456789 UTC' as utc_ts,
    TIMESTAMP '2024-01-15 12:30:45.123456789 America/Los_Angeles' as la_ts,
    CAST('2024-01-15 12:30:45.123456789' AS TIMESTAMP_NTZ) as ntz_ts;

-- Edge cases
SELECT
    TIMESTAMP '1970-01-01 00:00:00 UTC' as epoch,
    TIMESTAMP '9999-12-31 23:59:59.999999999 UTC' as max_ts,
    TIMESTAMP '0001-01-01 00:00:00 UTC' as min_ts;
```

### 4.3 Complex Types

```sql
-- Array operations
SELECT
    ARRAY(1, 2, 3, NULL, 5) as int_array,
    ARRAY('a', 'b', NULL, 'd') as str_array,
    ARRAY(ARRAY(1, 2), ARRAY(3, 4)) as nested_array;

-- Map operations
SELECT
    MAP('a', 1, 'b', 2, 'c', NULL) as str_int_map,
    MAP(1, 'one', 2, 'two') as int_str_map;

-- Struct operations
SELECT
    STRUCT(1 as id, 'name' as name, NULL as value) as simple_struct,
    STRUCT(ARRAY(1,2,3) as arr, MAP('k','v') as m) as complex_struct;
```

---

## 5. Execution

### 5.1 Python Validation

```python
from databricks import sql
import json

def validate_query(query_id, connection):
    query = load_query(f"oracle/queries/{query_id}.sql")
    expected = load_expected(f"oracle/expected/{query_id}.json")

    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
        columns = cursor.description

    return compare_results(result, columns, expected, language='python')
```

### 5.2 Go Validation

```go
package main

import (
    "database/sql"
    _ "github.com/databricks/databricks-sql-go"
)

func validateQuery(queryID string, db *sql.DB) error {
    query := loadQuery("oracle/queries/" + queryID + ".sql")
    expected := loadExpected("oracle/expected/" + queryID + ".json")

    rows, err := db.Query(query)
    if err != nil {
        return err
    }
    defer rows.Close()

    return compareResults(rows, expected, "go")
}
```

### 5.3 Java Validation

```java
import java.sql.*;

public class Validator {
    public void validateQuery(String queryId, Connection conn) throws Exception {
        String query = loadQuery("oracle/queries/" + queryId + ".sql");
        JsonObject expected = loadExpected("oracle/expected/" + queryId + ".json");

        try (Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(query)) {
            compareResults(rs, expected, "java");
        }
    }
}
```

### 5.4 Node.js Validation

```typescript
import { DBSQLClient } from '@databricks/sql';

async function validateQuery(queryId: string, client: DBSQLClient) {
    const query = await loadQuery(`oracle/queries/${queryId}.sql`);
    const expected = await loadExpected(`oracle/expected/${queryId}.json`);

    const session = await client.openSession();
    const operation = await session.executeStatement(query);
    const result = await operation.fetchAll();

    return compareResults(result, expected, 'nodejs');
}
```

---

## 6. Falsification Checklist

### 6.1 Data Type Mapping
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| DT-001 | BOOLEAN across languages | Same value | | |
| DT-002 | BIGINT boundaries | Same value | | |
| DT-003 | DOUBLE precision | Within 1e-15 | | |
| DT-004 | DECIMAL(38,30) precision | Exact string | | |
| DT-005 | TIMESTAMP timezone | Same instant | | |
| DT-006 | TIMESTAMP_NTZ | Same local time | | |
| DT-007 | ARRAY with NULLs | Same structure | | |
| DT-008 | MAP with NULL values | Same structure | | |
| DT-009 | Nested STRUCT | Same hierarchy | | |
| DT-010 | BINARY data | Same bytes | | |

### 6.2 Query Execution
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| QE-001 | Simple SELECT | Same rows | | |
| QE-002 | WHERE filtering | Same rows | | |
| QE-003 | JOIN results | Same rows | | |
| QE-004 | Aggregates | Same values | | |
| QE-005 | ORDER BY | Same order | | |
| QE-006 | LIMIT/OFFSET | Same subset | | |
| QE-007 | Set operations | Same rows | | |
| QE-008 | Subqueries | Same rows | | |
| QE-009 | Window functions | Same values | | |
| QE-010 | CTEs | Same rows | | |

### 6.3 NULL Handling
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| NL-001 | NULL column value | Language null | | |
| NL-002 | NULL in SUM | Excluded | | |
| NL-003 | NULL = NULL | NULL (not true) | | |
| NL-004 | COALESCE(NULL, 1) | 1 | | |
| NL-005 | ARRAY(1, NULL) | [1, null] | | |

### 6.4 Error Handling
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| ER-001 | Syntax error | Error thrown | | |
| ER-002 | Table not found | Error thrown | | |
| ER-003 | Column not found | Error thrown | | |
| ER-004 | Type mismatch | Error thrown | | |
| ER-005 | Permission denied | Error thrown | | |

### 6.5 Parameterized Queries
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| PQ-001 | String with quotes | Escaped | | |
| PQ-002 | Integer binding | Correct type | | |
| PQ-003 | Timestamp binding | Correct TZ | | |
| PQ-004 | Array parameter | Serialized | | |
| PQ-005 | NULL parameter | IS NULL | | |

---

## 7. Known Divergences

| Area | Python | Go | Java | Node.js | Reason |
|------|--------|-----|------|---------|--------|
| Decimal | Decimal | decimal.Decimal | BigDecimal | string | Language types |
| DateTime | datetime | time.Time | Instant | Date | Language stdlib |
| BIGINT | int | int64 | long | bigint | Language types |
| NULL | None | nil | null | null | Language idiom |

---

## References

- Databricks SQL Reference: https://docs.databricks.com/sql/language-manual/
- JDBC 4.3 Specification
- database/sql Go package
- Python DB-API 2.0 (PEP 249)

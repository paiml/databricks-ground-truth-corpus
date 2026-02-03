# Terraform Provider Databricks Oracle

**Version:** 1.0.0
**Date:** 2026-02-03
**Methodology:** Popperian Falsification

---

## 1. Overview

The Databricks Terraform Provider enables Infrastructure as Code for Databricks resources.

### Provider Under Test

| Provider | Language | Repository | Stars |
|----------|----------|------------|-------|
| terraform-provider-databricks | Go | databricks/terraform-provider-databricks | 569 |

---

## 2. Resource Validation Categories

### 2.1 Compute Resources

| ID | Resource | Test | Expected |
|----|----------|------|----------|
| CP-001 | databricks_cluster | Create | Cluster running |
| CP-002 | databricks_cluster | Update | Settings applied |
| CP-003 | databricks_cluster | Delete | Cluster terminated |
| CP-004 | databricks_instance_pool | Create | Pool created |
| CP-005 | databricks_cluster_policy | Create | Policy enforced |

### 2.2 Workspace Resources

| ID | Resource | Test | Expected |
|----|----------|------|----------|
| WS-001 | databricks_notebook | Create | Notebook created |
| WS-002 | databricks_notebook | Update | Content updated |
| WS-003 | databricks_directory | Create | Directory exists |
| WS-004 | databricks_repo | Create | Repo synced |
| WS-005 | databricks_workspace_file | Create | File uploaded |

### 2.3 Jobs Resources

| ID | Resource | Test | Expected |
|----|----------|------|----------|
| JB-001 | databricks_job | Create | Job created |
| JB-002 | databricks_job | Update | Settings applied |
| JB-003 | databricks_job | Delete | Job removed |
| JB-004 | databricks_job | Schedule | Triggers work |

### 2.4 SQL Resources

| ID | Resource | Test | Expected |
|----|----------|------|----------|
| SQ-001 | databricks_sql_warehouse | Create | Warehouse running |
| SQ-002 | databricks_sql_query | Create | Query saved |
| SQ-003 | databricks_sql_dashboard | Create | Dashboard exists |
| SQ-004 | databricks_sql_alert | Create | Alert active |
| SQ-005 | databricks_sql_permissions | Apply | Permissions set |

### 2.5 Unity Catalog Resources

| ID | Resource | Test | Expected |
|----|----------|------|----------|
| UC-001 | databricks_catalog | Create | Catalog exists |
| UC-002 | databricks_schema | Create | Schema exists |
| UC-003 | databricks_table | Create | Table exists |
| UC-004 | databricks_grants | Apply | Grants applied |
| UC-005 | databricks_storage_credential | Create | Credential stored |

### 2.6 MLflow Resources

| ID | Resource | Test | Expected |
|----|----------|------|----------|
| ML-001 | databricks_mlflow_experiment | Create | Experiment exists |
| ML-002 | databricks_mlflow_model | Create | Model registered |
| ML-003 | databricks_mlflow_webhook | Create | Webhook active |
| ML-004 | databricks_model_serving | Create | Endpoint serving |

### 2.7 Security Resources

| ID | Resource | Test | Expected |
|----|----------|------|----------|
| SC-001 | databricks_secret_scope | Create | Scope exists |
| SC-002 | databricks_secret | Create | Secret stored |
| SC-003 | databricks_token | Create | Token generated |
| SC-004 | databricks_permissions | Apply | Permissions set |
| SC-005 | databricks_ip_access_list | Create | List enforced |

---

## 3. State Management Tests

### 3.1 Plan Accuracy

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| PL-001 | Plan shows correct diff | No surprises | Exact |
| PL-002 | Plan detects drift | External changes shown | Exact |
| PL-003 | Plan is idempotent | No changes when up-to-date | Exact |

### 3.2 Import Functionality

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| IM-001 | Import existing cluster | State matches reality | Exact |
| IM-002 | Import existing job | State matches reality | Exact |
| IM-003 | Import existing warehouse | State matches reality | Exact |

### 3.3 Destroy Behavior

| ID | Test | Expected | Tolerance |
|----|------|----------|-----------|
| DS-001 | Destroy cluster | Cluster terminated | Exact |
| DS-002 | Destroy job | Job deleted | Exact |
| DS-003 | Destroy dependent resources | Correct order | Exact |

---

## 4. Golden Corpus Structure

```
terraform/
├── oracle/
│   ├── configs/
│   │   ├── cluster_basic.tf
│   │   ├── cluster_autoscale.tf
│   │   ├── job_simple.tf
│   │   ├── unity_catalog.tf
│   │   └── ...
│   ├── plans/
│   │   ├── cluster_basic.plan.json
│   │   └── ...
│   ├── states/
│   │   ├── cluster_basic.tfstate
│   │   └── ...
│   └── manifest.json
├── specs/
│   └── terraform-provider-oracle.md
└── scripts/
    ├── capture_golden.sh
    └── validate_provider.sh
```

### Sample Config

```hcl
# configs/cluster_basic.tf
resource "databricks_cluster" "test" {
  cluster_name            = "test-cluster"
  spark_version          = "13.3.x-scala2.12"
  node_type_id           = "i3.xlarge"
  autotermination_minutes = 10
  num_workers            = 2
}
```

---

## 5. Falsification Checklist

### 5.1 Compute Resources
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| CP-001 | Create cluster | Running | | |
| CP-002 | Update cluster | Applied | | |
| CP-003 | Delete cluster | Terminated | | |
| CP-004 | Create pool | Created | | |
| CP-005 | Create policy | Enforced | | |

### 5.2 Workspace Resources
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| WS-001 | Create notebook | Created | | |
| WS-002 | Update notebook | Updated | | |
| WS-003 | Create directory | Exists | | |
| WS-004 | Create repo | Synced | | |
| WS-005 | Create file | Uploaded | | |

### 5.3 State Management
| ID | Falsification Attempt | Expected | Actual | Pass |
|----|----------------------|----------|--------|------|
| PL-001 | Plan accuracy | Correct | | |
| PL-002 | Drift detection | Detected | | |
| PL-003 | Idempotency | No changes | | |
| IM-001 | Import cluster | Matches | | |
| DS-001 | Destroy cluster | Terminated | | |

---

## References

- Terraform Provider Docs: https://registry.terraform.io/providers/databricks/databricks
- Terraform Provider Repo: https://github.com/databricks/terraform-provider-databricks

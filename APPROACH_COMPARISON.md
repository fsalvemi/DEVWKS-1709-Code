# Approach Comparison: Three Methods for Catalyst Center Automation

This document compares three different approaches to deploying the same infrastructure (35 resources) to Cisco Catalyst Center:

1. **NAC Module** - Using the Network-as-Code Terraform Module with YAML configuration
2. **Native Terraform** - Using the CiscoDevNet Catalyst Center Terraform Provider
3. **Native API** - Direct REST API calls with Python

## 📊 Lines of Code Comparison

| Approach | Lines of Code | Complexity |
|----------|---------------|------------|
| **NAC Module** (YAML + minimal HCL) | ~183 lines | Low |
| **Native Terraform** (HCL) | ~445 lines | Medium-High |
| **Native API** (Python) | ~1,286 lines | High |

The NAC Module approach requires **7x less code** than Native API and **2.4x less code** than Native Terraform.

## 🔄 Feature Comparison Matrix

| Feature | NAC Module | Native Terraform | Native API |
|---------|------------|-----------------|-----------|
| **Declarative Approach** | ✅ Yes | ✅ Yes | ❌ No (Imperative) |
| **Idempotency** | ✅ Native | ✅ Native | ⚠️ Manual implementation |
| **State Tracking** | ✅ Built-in (tfstate) | ✅ Built-in (tfstate) | ❌ No (must implement) |
| **Full Destroy** | ✅ `terraform destroy` | ✅ `terraform destroy` | ⚠️ Manual (delete script) |
| **Partial Rollback** | ✅ Edit YAML + apply | ✅ Edit HCL + apply | ❌ Complex (manual API calls) |
| **Human-Readable Config** | ✅ YAML files | ⚠️ HCL syntax | ⚠️ Code-based |
| **Schema Validation** | ✅ `nac-validate` + JSON Schema + IntelliSense | ⚠️ `terraform validate` (syntax only) | ❌ Runtime errors only |
| **Dependency Management** | ✅ Automatic | ⚠️ ID-based references | ❌ Manual ordering |
| **Change Preview** | ✅ `terraform plan` | ✅ `terraform plan` | ❌ No |

## 📝 Detailed Comparison

### 1. Declarative vs Imperative Approach

| Approach | Style | Description |
|----------|-------|-------------|
| **NAC Module** | Declarative | You define desired state in intuitive YAML; module handles all API complexity |
| **Native Terraform** | Declarative | You define desired state, but must understand provider schema and manage ID references |
| **Native API** | Imperative | You write step-by-step instructions: "Create area A, then create building B, then create floor C..." |

### 2. Idempotency

| Approach | Idempotency | Notes |
|----------|-------------|-------|
| **NAC Module** | ✅ Native | Inherits Terraform's idempotency with simplified configuration |
| **Native Terraform** | ✅ Native | Terraform compares current state with desired state and only makes necessary changes |
| **Native API** | ⚠️ Manual | We had to add `if exists, skip` checks for each resource type. Without this, running the script twice would fail or create duplicates. |

### 3. State Tracking

| Approach | State Tracking | Implementation |
|----------|----------------|----------------|
| **NAC Module** | ✅ terraform.tfstate | Same as Native Terraform |
| **Native Terraform** | ✅ terraform.tfstate | Automatic tracking of all managed resources |
| **Native API** | ❌ None | Script has no memory of previous runs. Added `status` command to query current state from Catalyst Center. |

### 4. Configuration Complexity

| Approach | Configuration Style | Example |
|----------|---------------------|---------|
| **NAC Module** | Human-readable YAML | `parent_name: Global/United States/Golden Hills Campus` |
| **Native Terraform** | HCL with ID references | `parent_id = catalystcenter_area.golden_hills_campus.id` |
| **Native API** | Python dictionaries and function calls | `cc.create_building("Sunset Tower", "Global/United States/...", 34.099, -118.366, "address", "country")` |

### 5. Making Changes

| Approach | Process to Add a New Building |
|----------|------------------------------|
| **NAC Module** | Add 5 lines of YAML to existing file, run `terraform apply` |
| **Native Terraform** | Add new resource block with correct ID references, run `terraform plan/apply` |
| **Native API** | Add new function call in correct order, ensure all dependencies exist, run script |

### 6. Rollback Capabilities

#### Full Destroy (Remove All Resources)

| Approach | Command | Complexity |
|----------|---------|------------|
| **NAC Module** | `terraform destroy` | ✅ Single command, handles dependencies automatically |
| **Native Terraform** | `terraform destroy` | ✅ Single command, handles dependencies automatically |
| **Native API** | `python script.py --delete` | ⚠️ Required custom implementation with dependency ordering |

#### Partial Rollback (Undo a Specific Change)

| Approach | Process | Complexity |
|----------|---------|------------|
| **NAC Module** | Remove/modify lines in YAML file, run `terraform apply` | ✅ Simple - edit human-readable YAML, Terraform calculates and applies delta |
| **Native Terraform** | Remove/modify resource block in HCL, run `terraform apply` | ⚠️ Medium - must understand ID references and ensure no orphaned dependencies |
| **Native API** | Write custom deletion logic for specific resources | ❌ Complex - must track what was changed, call correct delete endpoints, handle dependencies manually |

**Example**: To remove a single floor that was added by mistake:

- **NAC Module**: Delete the 3-line floor entry from YAML, run `terraform apply`
- **Native Terraform**: Delete the `catalystcenter_floor` resource block, update any references, run `terraform apply`
- **Native API**: Find the floor ID via API, call DELETE endpoint, verify no dependent resources exist

### 7. Schema Validation

Schema validation helps catch configuration errors **before deployment**. The three approaches offer very different levels of validation:

| Approach | Validation Tool | When Errors Are Caught | Validation Scope |
|----------|-----------------|----------------------|------------------|
| **NAC Module** | `nac-validate` + JSON Schema + IntelliSense | While editing (IDE) + pre-commit + pre-apply | Syntactic + Semantic |
| **Native Terraform** | `terraform validate` | Before apply | Syntactic only |
| **Native API** | None | Runtime (after API call fails) | None |

#### NAC Module: Multi-Layer Validation

The NAC Module provides the most comprehensive validation through multiple tools:

1. **IntelliSense in VS Code**: Files with `.nac.yaml` suffix get real-time validation and auto-completion as you type. The JSON Schema checks attribute names, types, and required fields immediately.

2. **nac-validate CLI**: A dedicated tool for syntactic and semantic validation of YAML files. It validates against a Yamale schema and can run custom Python rules for business logic validation.

```bash
nac-validate data/
```

3. **Pre-commit Integration**: Can be added as a git pre-commit hook to prevent invalid configurations from being committed.

> **Learn More**: [nac-validate Documentation](https://netascode.cisco.com/docs/tools/nac-validate/overview/)

#### Native Terraform: Basic Syntax Validation

`terraform validate` checks HCL syntax and provider schema compliance:

```bash
terraform validate
```

**What it catches:**
- Missing required arguments
- Unknown attribute names
- Type mismatches (string vs number)
- Invalid resource references

**What it misses:**
- Business logic errors (invalid IP ranges, duplicate names)
- API-specific constraints
- Cross-resource semantic validation

#### Native API: No Pre-Deployment Validation

With the Native API approach, errors are only discovered at runtime when the API call fails. This leads to:
- Trial-and-error debugging cycles
- Cryptic API error messages
- Partial deployments when errors occur mid-script

### 8. Error Handling & Debugging

| Approach | Error Discovery | Debugging Experience |
|----------|-----------------|---------------------|
| **NAC Module** | Schema validation + `terraform plan` | First-time success with IntelliSense guidance |
| **Native Terraform** | `terraform plan` catches some issues | Schema changes between provider versions required complete rewrite (0.3.3 → 0.4.5) |
| **Native API** | Runtime only, cryptic API errors | Required 5+ iterations to fix payload format, task monitoring, authentication issues |

## 🔧 Development Experience

### NAC Module Experience

1. **Intuitive YAML** - Configuration mirrors network hierarchy naturally
2. **Schema Validation** - `.nac.yaml` suffix enables IntelliSense in VS Code
3. **No Provider Schema Knowledge** - Module abstracts API complexity
4. **Version Stability** - Module handles provider changes internally

### Native Terraform Challenges Encountered

1. **Schema Knowledge** - Required deep understanding of provider schema
2. **Breaking Changes** - Provider upgrade (0.3.3 → 0.4.5) required complete rewrite:
   - `parent_name` → `parent_id`
   - `ip_subnet` → `address_space_subnet` + `address_space_prefix_length`
   - New required fields (`units_of_measure` for floors)
3. **ID References** - Must use resource IDs, not human-readable names
4. **Data Source Required** - Needed `data.catalystcenter_site.global` to get Global site ID

### Native API Challenges Encountered

1. **API Endpoint Discovery** - Had to find working endpoints (`/api/v2/ippool` vs `/dna/intent/api/v1/global-pool`)
2. **Task Monitoring** - Implemented async task polling for each operation
3. **Authentication** - Added token refresh and retry logic
4. **Idempotency** - Manually added existence checks for each resource type
5. **State Checking** - Created separate `status` command to query current state

## 📈 Recommendation

| Use Case | Recommended Approach |
|----------|---------------------|
| **Production Deployments** | NAC Module - Lowest complexity, best maintainability |
| **Large-Scale Deployments** | NAC Module - Bulk API support, declarative state management |
| **Existing Terraform Expertise** | Native Terraform - Familiar tooling, but higher complexity |
| **Learning Catalyst Center APIs** | Native API - Full visibility into API operations |
| **Custom Integrations** | Native API - Maximum flexibility |

## 🔗 Resources

- **NAC Module**: [terraform-catalystcenter-nac-catalystcenter](https://registry.terraform.io/modules/netascode/nac-catalystcenter/catalystcenter/latest)
- **nac-validate Tool**: [netascode.cisco.com/docs/tools/nac-validate](https://netascode.cisco.com/docs/tools/nac-validate/overview/)
- **Catalyst Center Provider**: [CiscoDevNet/catalystcenter](https://registry.terraform.io/providers/CiscoDevNet/catalystcenter/latest)
- **Catalyst Center API Docs**: [developer.cisco.com](https://developer.cisco.com/docs/dna-center/)
- **Network-as-Code Documentation**: [netascode.cisco.com](https://netascode.cisco.com/)

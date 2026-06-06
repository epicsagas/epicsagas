---
name: env-test
description: "Tests that tools and products work outside the user's optimized development environment. Generates a compatibility checklist for lower-spec or general-purpose environments. Triggers on: 'env test', 'compatibility check', 'works on other machines', 'low spec test', 'production ready'."
---

# Env Test — External Environment Validation

Verify that the product works outside the developer's optimized machine. If it only works on YOUR machine, it's not a product — it's a demo.

## When to Trigger

**Auto-trigger**: User says "it works on my machine", or when deployment/sharing is mentioned without testing on other environments.

**Explicit** (`/env-test`): User wants to verify cross-environment compatibility before release, or suspects environment-specific issues.

## Constraints (NON-NEGOTIABLE)

1. **Test on at least 2 non-primary environments** — not just a different terminal window
2. **Include at least one constrained environment** — less RAM, slower CPU, different OS
3. **Fresh install test** — clone from scratch, install dependencies, run. No cached state.
4. **Document every failure** — "works mostly" is not passing
5. **Answer in Korean** unless user writes in English

## Process

### Step 1: Identify the primary environment

Document the user's development environment:

```markdown
## Primary Environment
- **OS**: {e.g., macOS Sequoia 15.5}
- **Hardware**: {e.g., Mac Studio M4 Max, 128GB RAM}
- **Shell**: {e.g., zsh 5.9}
- **Language runtime**: {e.g., Rust 1.85, Node 22}
- **Package manager**: {e.g., cargo, brew, mise}
- **Key dependencies**: {list}
```

### Step 2: Generate test matrix

Create environments to test against:

| Environment Type | Examples | Why test |
|-----------------|----------|----------|
| **Constrained hardware** | 8GB RAM laptop, Raspberry Pi, cloud VM (t3.small) | Reveals memory and performance assumptions |
| **Different OS** | Linux (Ubuntu), Windows (WSL), older macOS | Reveals platform-specific code |
| **Clean environment** | Fresh Docker container, new cloud instance | Reveals hidden dependency on local config |
| **Older runtime** | Previous LTS version of language runtime | Reveals version-specific features |

Select at least 2 environments from different rows.

### Step 3: Test checklist

For each environment, run through:

```markdown
## Test: {environment name}

### Setup
- [ ] Clone repository from scratch
- [ ] Install dependencies without errors
- [ ] Build succeeds
- [ ] Tests pass

### Runtime
- [ ] Application starts
- [ ] Core workflow completes
- [ ] No hardcoded paths (/Users/..., ~/specific/...)
- [ ] No platform-specific assumptions (case sensitivity, line endings)
- [ ] Performance acceptable (not just "works")

### Configuration
- [ ] Default configuration works without modification
- [ ] Environment variables documented
- [ ] No secrets in code or config files
- [ ] README instructions are accurate

### Result
- **PASS**: All checks green
- **PARTIAL**: Core works, some features broken
- **FAIL**: Cannot run at all
```

### Step 4: Gap report

For each failure:

```markdown
## Environment Gap: {environment}

| Check | Result | Root Cause | Fix Effort |
|-------|--------|------------|------------|
| {check} | ❌ | {why it failed} | {hours/days} |

## Hidden Dependencies Found
- {dependency the user didn't realize they relied on}

## Assumptions Violated
- {assumption that doesn't hold in this environment}
```

### Step 5: Record

```bash
mkdir -p env-test
```

Write to `env-test/TEST-{timestamp}.md`.

## Anti-Rationalization

| Excuse | Rebuttal | Do instead |
|--------|----------|-----------|
| "Our target users have good machines" | Your target users also have IT-managed laptops with different configs. | Test on a generic corporate laptop setup. |
| "It's a CLI tool, it works everywhere" | CLIs depend on shell version, PATH config, and system libraries. | Docker from scratch is the test. |
| "We'll fix cross-platform issues later" | "Later" becomes "never" 90% of the time. | Test now. Fix now. Ship once. |
| "I don't have access to other environments" | Docker is free. Cloud VMs cost cents per hour. | `docker run -it ubuntu:latest` is one command. |
| "CI tests on Linux already" | CI is a controlled environment, not a user's machine. | CI passes ≠ users succeed. Test user-representative setups. |

## Evidence Required

- [ ] Primary environment documented
- [ ] Test matrix generated with ≥2 environments
- [ ] Each environment tested with full checklist
- [ ] All failures documented with root cause
- [ ] Hidden dependencies identified
- [ ] Test results recorded to file

## Red Flags

- Only tested on different terminals of the same machine
- All tests "PASS" on first try (likely not testing thoroughly)
- Skipped the "constrained environment" row
- README instructions didn't work in clean environment
- Hardcoded paths found in code or config

## Agent Instructions

### Do
- Push for the constrained environment test — it reveals the most
- Test the README instructions literally — do exactly what they say
- Flag hardcoded paths aggressively
- Include a Dockerfile-based test for reproducibility
- Follow up on whether the gaps were actually fixed

### Do Not
- Accept testing only on the primary machine
- Let the user skip the clean install test
- Ignore performance differences between environments
- Treat "works but slow" as PASS on constrained hardware
- Generate the test plan without actually running it

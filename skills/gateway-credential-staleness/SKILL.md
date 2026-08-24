---
name: "gateway-credential-staleness"
description: "When a gateway-managed credential returns an auth-class error (401/403/'deactivated'/'invalid'), check shell env staleness before debugging the key itself."
---

# Gateway credential staleness on auth failures

When a credential managed by the OpenClaw gateway returns an auth-class error (401/403/"deactivated"/"invalid token"), the cause is usually a stale shell environment, not a bad credential value.

## Why

The gateway writes managed credentials to `~/.openclaw/service-env/ai.openclaw.gateway.env`. Long-running agent shells inherit their environment at startup. When the file is updated — a key regenerated, a token rotated, a new credential added — the file changes but existing shells keep their old values until they `source` the file again. No automatic reload exists.

## Procedure

1. Compare the process env value against the gateway file value.
   - File: `grep "^<CRED>=" ~/.openclaw/service-env/ai.openclaw.gateway.env | head -c 12` (peek at most 12 chars; never print full secrets to logs)
   - Shell: `echo "\$<CRED>" | head -c 12`
2. If they differ, run `source ~/.openclaw/service-env/ai.openclaw.gateway.env` in the same shell, then retry the failing call.
3. If the call still fails after `source`, the credential itself is genuinely bad. Investigate upstream (revoked, wrong scope, expired).

Completion criterion: the failing call succeeds after step 2, OR step 1 shows no difference and step 2 is a confirmed no-op.

## Don't

- Rotate or regenerate the credential before checking env staleness. Regeneration does not refresh shell env; the agent still holds the old value until reload.
- Trust a manual curl that succeeded from a fresh shell as evidence that the agent's env is correct. They are different shells with different env.
- Spend more than two exec calls on env-vs-credential confusion before doing step 1. A 403 is almost always stale env, not a real key problem.

## Trigger phrases

Any auth-class error from a service whose credential lives in the gateway env: "API key deactivated", "401 Unauthorized", "403 Forbidden", "invalid token", "credential not found".

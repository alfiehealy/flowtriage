# Credential Handling Standard (SEC-04)

## Policy
Secrets, API keys, tokens, and connection strings MUST NOT appear in:
- Flow definitions (action inputs, headers, body, variables)
- Run history comments or notes
- Environment variable *values* of type "Text" (use type "Secret" backed by Azure Key Vault)

## Why this is CRITICAL severity
Flow definitions are exportable by any co-owner and readable in run history.
A hardcoded key in an HTTP action header is equivalent to publishing it
internally. Per rubric v2.1 this is CRITICAL (score 90+).

## Detection guidance
Search HTTP action inputs for header names: x-api-key, Authorization,
Ocp-Apim-Subscription-Key, client_secret. Any literal string value (rather
than a Key Vault or environment-variable reference) is a violation.

## Remediation pattern
1. Rotate the exposed key immediately at the source system.
2. Store the new key in Azure Key Vault.
3. Reference it via an environment variable of type Secret, or call the
   API through a custom connector using OAuth/managed identity.

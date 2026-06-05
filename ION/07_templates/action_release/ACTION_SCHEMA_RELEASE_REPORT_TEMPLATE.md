# Action Schema Release Report

Domain: `CUSTOM_GPT_ACTION_RELEASE`
Status: candidate release report template.

## Required fields

- canonical schema path
- schema SHA256
- operation count
- old/core operations preserved
- new operations added
- duplicate operationId check
- no-secret check
- server URL
- auth token source
- rollback sheet path
- AUTH_INVALID stop rule

## Rule

This report must be generated for the full canonical schema. It must not be
generated from a fragment or feature-only OpenAPI file.

# GPT Builder Rollback Sheet

Status: candidate rollback sheet template.

## Required sections

- rollback trigger
- known-good full schema path
- freeze rule
- missing operationId response
- auth failure response
- non-claims

## Rule

If rollback state is uncertain, freeze Actions instead of trying another schema.

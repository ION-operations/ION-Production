# ION Project Hash Identity and Helixion Handshake

Use `ion_project_hash` as public project identity, never as a password. Folder
key branches are non-secret pointers to validation, package, receipt, and
capability-request surfaces. They may be exported.

Helixion is the authorization source. A Custom GPT Action may send project hash,
package hash, branch hashes, and challenge nonce. Helixion must derive the user
from OAuth/session/approval, not from chat text. Unauthorized hashes must not
reveal private metadata.

Recommended handshake:

1. GPT reads or creates `ION_PROJECT_IDENTITY.yaml`.
2. GPT sends hash plus branch/package proof plus challenge to Helixion.
3. Helixion authenticates or approves the user.
4. Helixion checks subject/project ACL.
5. Helixion returns a scoped context package or capability grant.
6. Capability grants are short-lived, scoped, receipt-required, and never exported.

One GPT can serve many users safely only when Helixion enforces subject plus
project access control server-side.

# Source-Ordered Fan-In Settlement

Merge order is source order, not branch completion order.

For each baton:
1. Verify required upstream batons were present.
2. Confirm/reject/extend downstream alerts.
3. Record upstream reopen alerts.
4. Escalate unresolved questions.
5. Produce settlement receipt.

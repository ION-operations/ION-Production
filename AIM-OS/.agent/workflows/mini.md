---
description: ION MINI capsule boot — read MINI, follow ROUTE, write PRE/POST capsules, update context
---
# SOS MINI Capsule Boot

// turbo-all

1. Read the current MINI capsule from `/home/sev/SOS/05_context/MINI.md`.
   - Parse the state fields (MISSION, PHASE, NOW, NEXT).
   - Parse the ROUTE block — extract every file path listed.

2. Follow every ROUTE entry in order:
   - Read `/home/sev/SOS/05_context/CAPSULE.md` (always first — the work log).
   - Read every additional file listed in the ROUTE.

3. Write a PRE capsule in chat acknowledging:
   - Current MISSION and PHASE.
   - What was loaded from ROUTE.
   - Any BLOCKERs found.
   - What the NEXT action is.

4. Begin work following the task described in NEXT.

5. At END of output, write POST capsule and update:
   - `cp /home/sev/SOS/05_context/CAPSULE.md /home/sev/SOS/05_context/history/$(date +%Y-%m-%d_%H%M%S)_CAPSULE.md`
   - Update `/home/sev/SOS/05_context/CAPSULE.md` with new WORK LOG entry.
   - Update `/home/sev/SOS/05_context/MINI.md` with new ROUTE for next task.

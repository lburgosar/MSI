# MSI coordination protocol

This directory is the asynchronous coordination bus between RAMON and AURO.

```text
RAMON -> AURO_HANDOFF.md -> GitHub -> AURO -> review/instruction
                                      |
                                      +-> Leandro decides when human judgment is required
```

- RAMON updates and pushes the handoff when completing every significant increment.
- AURO reads the handoff, follows its canonical references, and records a review or instruction through the agreed repository workflow.
- Leandro validates the product and makes consequential product or architecture decisions; he is not the document transport layer.
- Git provides persistence, ordering, authorship, and traceability.

An increment is incomplete until [AURO_HANDOFF.md](AURO_HANDOFF.md) reflects it. Keep that file short: it is an operational index, not a duplicate design document. [CURRENT_STATE.md](CURRENT_STATE.md) describes the global project state and [DECISIONS.md](DECISIONS.md) records only high-value decisions.

This file-based transport is intentionally simple and replaceable by native agent-to-agent coordination later.

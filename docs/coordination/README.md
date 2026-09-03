# MSI review entry point

Git/GitHub is the transport and source of truth between RAMON and AURO. This directory is only a concise operational index that helps AURO locate the checkpoint and evidence to inspect.

```text
RAMON -> tests -> commit/push -> GitHub
                                  |
                                  +-> AURO_HANDOFF.md (entry point)
                                             |
                                             +-> AURO independently audits Git evidence
                                                        |
                                                        +-> Leandro validates and decides
```

- RAMON updates and pushes the brief handoff when completing every significant increment.
- AURO uses it to find the relevant branch, checkpoint, code, documents and tests, then verifies the evidence independently.
- Leandro validates the product and makes consequential product or architecture decisions; he is not the document transport layer.
- Git provides persistence, ordering, authorship, and traceability.

An increment is incomplete until [AURO_HANDOFF.md](AURO_HANDOFF.md) reflects it. Keep that file short: it is an operational index, not a duplicate design document. [CURRENT_STATE.md](CURRENT_STATE.md) describes the global project state and [DECISIONS.md](DECISIONS.md) records only high-value decisions.

The handoff does not replace inspection and is not a second transport or source of truth.

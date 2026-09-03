# Mission lifecycle mapping

Status: proposal; no immediate Runtime state rename.

| MSI Next stage | V2.1 evidence/state | Gap / migration action |
|---|---|---|
| Intent | Home interview/configuration | Promote intent to explicit durable object |
| Spatial Definition | Demo operational area | Accept SpatialIntent geometry independent of route |
| Validation / Reconnaissance | No dedicated stage | Add confidence/freshness assessment and optional reconnaissance sub-mission |
| Refinement | Position editing/replan | Compare operator/interpreted/verified geometry |
| Simulation | Simulation engine used for execution demo | Add non-productive validation run and findings |
| Preflight | READY/BLOCKED/REQUIRES_DATA | Already explainable; consume simulation and environment findings |
| Resource Assignment | Planner assignment | Add proposal/override explanation lifecycle |
| Authorization | `authorized` | Present what/where/with what/time/consumption/risks |
| Execution | `running` | Introduce governed operational command dispatcher |
| Adaptation | decisions/replans/paused | Preserve; connect observations and explicit impacts |
| Outcome | `completed` + mission_summary | Expand requested/performed/changed/pending/learned |
| Learning / Memory | JSONL trace | Curate reviewed knowledge; never auto-change safety limits |

## Transition policy

Do not force every mission through reconnaissance. MSI evaluates map source, age, confidence, obstacles and required accuracy, then records `not_required`, `recommended` or `required` with reason. A reconnaissance is its own planned mission consuming time, battery and risk but no productive consumable.

## Compatibility strategy

Keep V2.1 status values and add a higher-level lifecycle projection in presentation/application services. Change Runtime states only after transitions and replay compatibility are tested.


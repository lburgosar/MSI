# Agent Lab Spike 001 — MSI NEXT Track A review

Date: 2026-09-03

Status: **completed as a viability test; review workflow did not complete**

Cost: **USD 0 additional**

## Question

Can a small read-only specialist workflow independently audit MSI NEXT Track A, using the current machine and already-authorized services, without paid APIs or a new infrastructure project?

## Experiment

Three read-only reviewers were started in parallel:

1. UX/operator experience;
2. GIS/geospatial correctness;
3. architecture and safety.

The intended next stages were critic, synthesis and human review. Agents were explicitly prohibited from modifying MSI or accepting the handoff as proof.

## Result

All three reviewers stopped before returning findings because the shared Codex usage limit was reached. No MSI files were modified and no credits were purchased. Critic and synthesis were not run because they would have had no specialist evidence to evaluate.

This is a valid negative result:

- role separation and parallel dispatch are easy with the existing Codex workflow;
- the workflow is not currently reliable for unattended or scheduled review under the available shared quota;
- adding more orchestration software would not create model capacity;
- ChatGPT Plus must not be treated as OpenAI API credit. OpenAI states that API billing is separate from ChatGPT subscriptions.

## Local baseline

- RAM: 15.9 GB.
- GPU: Intel HD Graphics 530, reported dedicated memory 1 GB.
- Available: Python.
- Not installed: Ollama, Docker, Node.js/npm.

These facts do not rule out a small local model, but they make useful latency and review quality uncertain. That capability must be benchmarked before relying on it.

## Platform screen

| Option | USD 0 path | Fit now | Decision |
|---|---|---|---|
| Existing Codex collaboration | Included usage only; no API | Fastest and already operational, but quota-coupled | Use opportunistically, not as unattended infrastructure |
| Langflow OSS | MIT; local Python package or Docker | Installable with current Python, but adds a large visual runtime and still needs a model | Do not install for this spike |
| Flowise self-hosted | Open-source, local/air-gapped option | Requires Node.js, currently absent; still needs a model | Do not install |
| AutoGen | Local Python orchestration | Good code-first abstraction, but model access remains separate | Keep as later adapter candidate |
| Ollama | Local Windows runtime | No token fees after installation; small-model feasibility on this hardware is unverified | READY — REQUIRES LOCAL INSTALL/BENCHMARK, not authorized by this spike |
| Paid provider APIs | Technically straightforward | Violates current budget constraint | Not permitted |

## Decision

Do not build or install an Agent Lab platform now. The minimum spike has answered the immediate question: orchestration is feasible, but dependable zero-additional-cost model execution is not yet demonstrated on this machine.

If Agent Lab is revisited, preserve a small provider-neutral workflow definition and benchmark one local model against one Track A review task before evaluating a visual platform. Stop if its review quality or turnaround does not save more effort than it consumes.

## MSI review status

This spike is **not** an AURO audit and produced no specialist verdict on Track A. Track A remains ready for AURO's independent review at [the canonical handoff](../coordination/AURO_HANDOFF.md).

## Sources

- [OpenAI: API billing is separate from ChatGPT](https://help.openai.com/en/articles/8156019-is-api-usage-included-in-chatgpt-subscriptions-even-if-i-have-a-paid-chatgpt-account)
- [Langflow local installation options and requirements](https://docs.langflow.org/get-started-installation)
- [Flowise self-hosting and local installation](https://docs.flowiseai.com/getting-started)
- [AutoGen official documentation](https://microsoft.github.io/autogen/)
- [Ollama for Windows and storage requirements](https://docs.ollama.com/windows)

# Resumable runs

Each run directory is a checkpointed execution workspace. The minimum durable files are:

- `run.json` — current stage, status, scenario version, input hash, and review gate;
- `events.jsonl` — append-only audit trail;
- `pbit-inventory.json` — immutable inspection evidence;
- `review.json` — questions, answers, and decisions;
- later: `design.json`, generated assets, validation evidence, and handoff artifacts.

Runs can be resumed by loading `run.json`, verifying the scenario version and input hash,
then continuing from the next incomplete stage.

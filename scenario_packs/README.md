# Scenario packs

Scenario packs are versioned, reusable migration definitions. They contain the
reference PBIT identity, approved design, target adapter, templates, evaluations,
and evidence needed to continue or reproduce a supported migration.

Execution state does not belong here. Each execution is stored under `runs/<run-id>`
and records its scenario ID/version, input hash, review decisions, events, and output
artifact hashes.

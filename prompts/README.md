# Runtime prompt library

These prompts are application assets, not instructions for the development
assistant. They are versioned, selected by `config/agent-registry.yml`, and
recorded in a run manifest whenever an agent makes a proposal or decision.

Every prompt must return structured JSON matching the stage output contract.
The agent may recommend changes, identify ambiguity, and ask questions; it may
not approve its own release, publish external assets, or silently discard
unsupported report behavior.

Each prompt defines its objective, allowed scope, input evidence, output
fields, confidence/assumption rules, escalation conditions, and deterministic
tools the agent may request.

# Agentic Shift-Left Risk Register

The application risk register contains generic product risks. Demo-specific
risks and evidence remain under the applicable directory in `examples/`.

| ID | Risk | Category | Likelihood | Impact | Rating | Status | Owner |
|---|---|---|---|---|---|---|---|
| ASL-R-001 | A generated migration may weaken source security behavior when the target access model is incomplete or ambiguous. | Security / Governance | Medium | High | High | Open | Security/data product owner — TBD |
| ASL-R-002 | Unsupported PBIT features may be omitted without the user understanding the impact. | Compatibility | Medium | High | High | Open | Product/BI owner — TBD |
| ASL-R-003 | LLM output may invent business meaning or mapping decisions. | AI quality | Medium | High | High | Open | Agent owner — TBD |

## Release control

The application must fail closed when a security mapping, unsupported feature,
or material semantic decision lacks evidence and human disposition.

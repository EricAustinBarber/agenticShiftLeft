---
skill_id: pbit-inspection
version: 1.0.0
---

# PBIT inspection skill

Purpose: safely inspect a Power BI template and produce a complete inventory.

Allowed tools: PBIT package reader, package validator, inventory extractor.

Must produce: package hash, inventory path, unsupported-feature findings, and
evidence references. Must not rewrite or overwrite the input package.

Failure behavior: stop on package validation errors or unclassified model
objects and create a review item.

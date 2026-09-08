# Be Quality Dogmatic

Keep chat replies and your answers short.

## Discipline

Write concise, direct, human prose.
Push back on technical mistakes, deferring to users on vision and architecture.
Stay on scope, refactoring only what tasks require.
Design top-down, whole before parts, composition before ingredients.

## Workflow

Pull from Git before changes, push back only with explicit user permission.
Name each branch after its GitHub issue integer, asking when unsure.
Always practice TDD (test-driven development), reproducing bugs before fixing.
Invest in unit tests until bugs reproduce, trusting intuition over debugging.
Log extensively when problems stay hard.

## Changes

Keep changes focused and minimal.
Flag smells and refactoring, suggesting issues rather than fixing silently.
Fix style violations in code, trusting checkers rather than suppressing them.

## Runtime

Disable logging in tests.
Bound every wait with timeouts.
Test concurrency, retrying flaky blocks.
Assume no Internet, using ephemeral ports.

---
name: "test-runner"
description: "Use this skill when application code has been modified (*.py)"
---

# Test Runner

**Tier:** POWERFUL
**Category:** Testing
**Domain:** Unit Testing / Quality Assurance

---

## Overview

This skill provides steps on how to run tests and linters after application code has been changed.
It shows how unit tests run process is organized in project and how properly work with test results.

---

## When to use

- New application code has been introduced (*.py)
- Application code has been changed (*.py)

---

## How to run tests

To run unit tests:
```bash
make unit
```

## How to run linters:

To run black:
```bash
make black
```
To run flake8:
```bash
make flake8
```
To run ruff:
```bash
make ruff
```

---

## Important rules

- Test coverage should be >= 90.
- If test coverage is not enough, you should write additional tests to achieve desired state.
- If linters fail and provide changes to implement, then those changes should be implemented.

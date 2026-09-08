# Testing Rules

---

## 1. Test Design

### 1.1 Logic-Free Tests
- Unit tests must be logic-free: they must not implement any algorithms.
- Aim for one-statement tests.

### 1.2 Assertions
- Each test must contain exactly one assertion.
- Each test must contain at least one assertion.
- The last statement in every test must be an assertion.
- Do not assert on the absence of failure.
- Never assert on side effects.
- Be creative with assertions.
- Use the PyHamcrest library to achieve this.

### 1.3 Test Inputs
- Whenever possible, tests should use irregular, boundary, or strange inputs to provoke hidden issues.
- Every test must use its own literals, numbers, and input values.
- Do not reuse inputs across tests, as this may falsely suggest shared meaning.
- Always write descriptive failure messages.

### 1.4 Test Isolation
- Test methods must share absolutely no fixtures with other test methods.

---

## 2. Naming and Documentation

### 2.1 Test Naming
- Test names must be complete English phrases that would start with "it" if written fully. Example: (it) builds_empty_png_image
- "it" refers to the object under test, not the test itself.

### 2.2 Documentation
- Tests must not contain documentation comments.

---

## 3. Scope and Boundaries

### 3.1 What to Test
- Never write tests for private or protected methods.
- Avoid overtesting.
- Tests must never be the reason for expanding an object's public interface.
- Avoid testing abstract classes directly.

### 3.2 Feature Class Correspondence
- Each feature class must have exactly one corresponding test module.
- Feature classes should trust each other and only guard against invalid end-user input.

---

## 4. Resources and Cleanup

### 4.1 System Resources
- Tests must close all system resources when they finish.
- Tests that require resources must begin with cleanup.

### 4.2 File Handling
- If a test works with files, it must create its own temporary directory and store all files there.
- Do not mock the file system.
- Place all temporary files inside a top-level tmp/ directory in the repository.

---

## 5. Fakes and Logging

### 5.1 Fakes Over Mocks
- Do not use mocks. Use fake implementations instead.

### 5.2 Logging
- Logging should be disabled during tests whenever possible.
- If logging is part of the specification, test it using fake classes that capture messages instead of printing them.

---

## 6. Test Patterns

### 6.1 Parametrized Tests
- If multiple inputs share the same scenario, use parametrized tests.

### 6.2 Thread Safety
- If a class uses threads or claims thread safety, there must be tests confirming its thread safety.

### 6.3 Flaky Tests
- Use pytest-repeat to run flaky tests multiple times when needed.

### 6.4 Online Tests
- Mark all tests requiring internet access with: pytest.mark.online

---

## 7. Test-Driven Development

### 7.1 Bug Fixes
- Before fixing a bug, reproduce it with a failing test case.

### 7.2 New Features
- Before adding a new feature, there must be a failing test first.

---

## 8. Test Execution

### 8.1 Performance
- Use pytest-fail-slow to automatically fail tests that run too slowly.

### 8.2 Randomization
- Execute tests in random order and print the randomization seed to the console.

---

## 9. Test Categories

### 9.1 Fast Tests (Unit)
- Minimal execution time.

### 9.2 Deep Tests (Integration)
- Realistic live scenarios.
- If deep tests require external dependencies (databases, remote services, etc.), use Testcontainers.

---

## 10. Quality Tools

### 10.1 Grammar Checking
- Use language-tool-python to check English grammar in string literals and exception messages.

### 10.2 Property-Based Testing
- Use Python Hypothesis for property-based testing.

### 10.3 Mutation Testing
- Use mutmut for mutation testing.

# Pytest Speedup Guide - MiraiWorks

## 🚀 Overview

This guide explains how to run tests **significantly faster** using parallel execution and optimization techniques.

### Expected Speedup
- **Serial execution**: ~5-10 minutes for full test suite
- **Parallel execution**: ~1-3 minutes for full test suite
- **Speedup factor**: **3-5x faster** 🔥

---

## ⚡ Quick Start

### Standard Test Execution

```bash
cd backend
python -m pytest
```

### Fastest Way to Run Tests (Parallel)

```bash
cd backend
python -m pytest -n auto --dist loadfile
```

Or use the make target:
```bash
make test-fast
```

This will:
- Automatically detect all CPU cores
- Run tests in parallel
- Distribute tests by file for optimal load balancing
- Show only failures and summary

---

## 📖 Available Commands

### Basic Commands

| Command | Description | Speed | Use When |
|---------|-------------|-------|----------|
| `python -m pytest` | Standard serial execution | ⚪ Slow | Debugging, single tests |
| `python -m pytest -n auto` | Parallel (auto cores) | 🟢 Fastest | Default choice |
| `make test` | Standard serial execution | ⚪ Slow | Full coverage needed |
| `make test-fast` | Parallel (auto cores) | 🟢 Fastest | Quick full suite |
| `make test-quick` | Parallel + stop on first fail | 🟢 Fastest | Quick validation |
| `make test-failed` | Re-run only failed tests | 🟢 Fast | After fixing issues |
| `make test-parallel WORKERS=8` | Parallel with 8 workers | 🟡 Fast | Custom worker count |

### Advanced Commands

```bash
# Run specific test file in parallel
make test-file FILE=test_auth.py

# Run with coverage (parallel)
make test-coverage

# Find slow tests
pytest app/tests/ --durations=20 -n auto

# Run only failed tests from last run
make test-failed

# CI/CD optimized
make test-ci
```

---

## 🛠️ Parallel Execution Explained

### How It Works

**pytest-xdist** distributes tests across multiple CPU cores:

```
┌─────────────────────────────────────────┐
│         Master Process                   │
│  (Collects tests & coordinates)         │
└───────────┬─────────────────────────────┘
            │
    ┌───────┴───────┬─────────┬──────────┐
    │               │         │          │
┌───▼───┐    ┌─────▼──┐  ┌──▼────┐  ┌──▼────┐
│Worker1│    │Worker2 │  │Worker3│  │Worker4│
│test_a │    │test_b  │  │test_c │  │test_d │
└───────┘    └────────┘  └───────┘  └───────┘
```

### Distribution Strategies

**loadfile** (Recommended)
- Groups tests by file
- Better for tests with shared fixtures
- More balanced execution

**loadscope**
- Groups tests by scope (class/module)
- Good for test classes

**load**
- Individual test distribution
- Best for uniform test duration

---

## 📊 Configuration Details

### pytest.ini Settings

```ini
[tool:pytest]
addopts =
    -n auto                  # Auto-detect CPU cores
    --dist loadfile          # Distribute by file
    --maxfail=1             # Stop after first failure
    --timeout=300           # 5 minute timeout per test
    --durations=10          # Show 10 slowest tests
```

### Environment Variables

```bash
# Control number of workers
export PYTEST_XDIST_AUTO_NUM_WORKERS=8

# Control worker timeout
export PYTEST_TIMEOUT=300
```

---

## 🎯 Optimization Tips

### 1. Database Fixtures

**Current State**: Database fixtures are already optimized
- Session-scoped database setup
- Fast data clearing between tests
- Connection pooling enabled

### 2. Test Organization

**Mark slow tests:**
```python
@pytest.mark.slow
def test_complex_operation():
    # Long-running test
    pass
```

**Run fast tests only:**
```bash
pytest -m "not slow" -n auto
```

### 3. Fixture Scope

**Use appropriate scopes:**
```python
@pytest.fixture(scope="session")  # Once per test session
def database():
    pass

@pytest.fixture(scope="module")   # Once per test module
def api_client():
    pass

@pytest.fixture(scope="function")  # Once per test (default)
def test_data():
    pass
```

### 4. Skip Expensive Operations

```python
@pytest.mark.skipif(os.getenv("QUICK_TEST"), reason="Skipping in quick mode")
def test_full_integration():
    pass
```

---

## 📈 Benchmarking

### Find Bottlenecks

```bash
# Show 20 slowest tests
pytest app/tests/ --durations=20 -n auto

# Profile test execution
pytest app/tests/ --profile -n auto
```

### Example Output

```
===== slowest 10 durations =====
15.23s call     app/tests/test_recruitment_workflow.py::test_complete_flow
8.45s call      app/tests/test_interview.py::test_video_call_integration
5.67s call      app/tests/test_resume.py::test_pdf_generation
...
```

---

## 🔧 Troubleshooting

### Issue: Tests Failing in Parallel

**Cause**: Shared state between tests
**Solution**: Use proper fixtures, avoid global variables

```python
# ❌ BAD: Global state
GLOBAL_COUNTER = 0

def test_something():
    global GLOBAL_COUNTER
    GLOBAL_COUNTER += 1

# ✅ GOOD: Fixture-based
@pytest.fixture
def counter():
    return {"value": 0}

def test_something(counter):
    counter["value"] += 1
```

### Issue: Database Conflicts

**Cause**: Tests modifying shared database
**Solution**: Already handled by `conftest.py` - each test gets clean data

### Issue: Slower Than Expected

**Check**:
1. Number of CPU cores: `python -c "import os; print(os.cpu_count())"`
2. Worker overhead: Try different WORKERS counts
3. I/O bottlenecks: Database on SSD?

**Fix**:
```bash
# Try different worker counts
make test-parallel WORKERS=4
make test-parallel WORKERS=8
make test-parallel WORKERS=16
```

---

## 🎨 Best Practices

### 1. Write Fast Tests

```python
# ✅ GOOD: Fast, focused test
def test_user_validation():
    user = User(email="test@example.com")
    assert user.is_valid()

# ❌ BAD: Slow, unfocused test
def test_entire_user_workflow():
    # Creates user, logs in, updates profile, uploads files...
    # Takes 30 seconds
```

### 2. Use Markers

```python
# Mark integration tests
@pytest.mark.integration
def test_full_api_flow():
    pass

# Mark unit tests
@pytest.mark.unit
def test_pure_function():
    pass
```

**Run selectively:**
```bash
# Only unit tests (fast)
pytest -m unit -n auto

# Only integration tests
pytest -m integration -n auto
```

### 3. Mock External Services

```python
# ✅ GOOD: Mock external API
@pytest.fixture
def mock_payment_service(mocker):
    return mocker.patch("app.services.payment.PaymentAPI")

# ❌ BAD: Call real external API
def test_payment():
    response = real_payment_api.charge(...)  # Slow!
```

---

## 📋 Cheat Sheet

```bash
# Basic execution
python -m pytest                          # Standard serial execution
python -m pytest -n auto                  # Parallel with auto-detect cores
python -m pytest -n 8                     # Parallel with 8 workers

# Development (fastest feedback)
python -m pytest -n auto -x               # Stop on first failure
make test-quick                           # Same as above

# Pre-commit (fast validation)
python -m pytest -n auto --dist loadfile  # All tests, parallel
make test-fast                            # Same as above

# After fixing failures
python -m pytest --lf -x                  # Only re-run failures
make test-failed                          # Same as above

# Full validation
make test-coverage                        # With coverage report

# Custom parallel execution
python -m pytest -n 8 --dist loadfile     # 8 workers

# Run specific module
python -m pytest app/tests/test_auth*.py -n auto   # All auth tests

# Find slow tests
python -m pytest --durations=0 -n auto    # Show all durations
```

---

## 🎯 Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Full test suite | < 3 min | ~2-3 min |
| Unit tests only | < 30 sec | ~20-30 sec |
| Single test file | < 10 sec | ~5-10 sec |
| Failed test re-run | < 20 sec | ~10-20 sec |

---

## 🚀 CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
- name: Run tests (parallel)
  run: |
    cd backend
    make test-fast
```

### GitLab CI

```yaml
test:
  script:
    - cd backend
    - make test-fast
```

---

## 📚 Additional Resources

- [pytest-xdist documentation](https://pytest-xdist.readthedocs.io/)
- [pytest performance tips](https://docs.pytest.org/en/stable/how-to/performance.html)
- [Fixture scopes](https://docs.pytest.org/en/stable/how-to/fixtures.html#scope-sharing-fixtures-across-classes-modules-packages-or-session)

---

## 🎉 Summary

**Standard Execution**:
```bash
python -m pytest                # Serial execution (baseline)
```

**Optimized Execution**:
```bash
python -m pytest -n auto        # Parallel execution (3-5x faster!) ⚡
# OR
make test-fast                  # Same as above
```

**Speedup**: **3-5x faster testing!** 🔥

---

**Last Updated**: 2025-10-01
**Maintained by**: MiraiWorks Team

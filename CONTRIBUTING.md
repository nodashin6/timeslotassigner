# Contributing to TimeSlotAssigner

We welcome contributions to TimeSlotAssigner! This document provides guidelines for contributing to the project.

## Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/yourusername/timeslotassigner.git
   cd timeslotassigner
   ```

2. **Install uv (if not already installed):**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Set up the development environment:**
   ```bash
   uv sync --dev
   ```

4. **Verify the setup:**
   ```bash
   uv run pytest
   uv run ruff check .
   uv run mypy timeslotassigner
   ```

## Development Workflow

### Code Standards

- **Python Version**: Python 3.12+ required
- **Code Style**: Use Ruff for formatting and linting
- **Type Safety**: All code must have proper type hints and pass mypy
- **Documentation**: All public APIs must have comprehensive docstrings with examples

### Running Tests

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=timeslotassigner

# Run specific test file
uv run pytest tests/test_calendar.py

# Run tests in verbose mode
uv run pytest -v
```

### Code Quality Checks

```bash
# Format code
uv run ruff format .

# Check linting
uv run ruff check .

# Type checking
uv run mypy timeslotassigner

# Run benchmarks
uv run python benchmarks.py
```

## Contributing Guidelines

### 1. Bug Reports

When filing a bug report, please include:

- **Python version and OS**
- **TimeSlotAssigner version**
- **Minimal code example** that reproduces the issue
- **Expected vs actual behavior**
- **Stack trace** (if applicable)

### 2. Feature Requests

For new features:

- **Describe the use case** and motivation
- **Propose the API design** with code examples
- **Consider performance implications** (maintain O(log N) characteristics)
- **Discuss backward compatibility**

### 3. Pull Requests

#### Before Submitting

- [ ] Tests pass: `uv run pytest`
- [ ] Code is formatted: `uv run ruff format .`
- [ ] Linting passes: `uv run ruff check .`
- [ ] Type checking passes: `uv run mypy timeslotassigner`
- [ ] Documentation is updated (if needed)
- [ ] Performance tests pass: `uv run python benchmarks.py`

#### PR Checklist

- [ ] **Clear description** of changes and motivation
- [ ] **Tests added/updated** for new functionality
- [ ] **Documentation updated** (docstrings, README, etc.)
- [ ] **Backward compatibility** maintained (or breaking changes justified)
- [ ] **Performance benchmarks** show no regressions

#### PR Guidelines

1. **Keep PRs focused**: One feature/fix per PR
2. **Write clear commit messages**: Use conventional commits format
3. **Add tests**: All new code must have comprehensive tests
4. **Update docs**: Keep documentation in sync with code changes
5. **Performance**: Maintain O(log N) characteristics for core operations

### 4. Code Architecture

#### Core Principles

- **O(log N) Performance**: All primary operations must maintain logarithmic time complexity
- **Type Safety**: Comprehensive type hints throughout
- **Immutable Public APIs**: Avoid breaking changes to existing APIs
- **Comprehensive Testing**: High test coverage with edge cases
- **Clear Documentation**: Self-documenting code with examples

#### Module Structure

```
timeslotassigner/
├── __init__.py          # Public API exports
├── calendar.py          # CalendarBase and Calendar classes
├── manager.py           # CalendarManager class  
├── exceptions.py        # Custom exceptions
└── utils.py            # Utility functions (if needed)
```

#### Adding New Features

1. **Design the API** with type hints and docstrings
2. **Implement core logic** maintaining O(log N) performance
3. **Add comprehensive tests** including edge cases
4. **Update documentation** and examples
5. **Add benchmarks** to verify performance characteristics

### 5. Testing Guidelines

#### Test Categories

- **Unit Tests**: Test individual methods and classes
- **Integration Tests**: Test interactions between components
- **Performance Tests**: Verify O(log N) characteristics
- **Edge Case Tests**: Boundary conditions and error cases

#### Test Naming

```python
def test_method_name_scenario():
    """Test description of what is being tested."""
    pass

def test_add_slot_success():
    """Test successful slot addition returns True."""
    pass

def test_add_slot_conflict():
    """Test slot addition with conflict returns False."""
    pass
```

#### Test Structure

```python
def test_example():
    """Test description."""
    # Arrange
    calendar = CalendarBase("test")
    
    # Act
    result = calendar.add_slot(10, 12, "meeting")
    
    # Assert
    assert result is True
    slots = calendar.get_all_slots()
    assert len(slots) == 1
    assert slots[0] == (10, 12, "meeting")
```

### 6. Documentation

#### Docstring Format

```python
def method_name(self, param: int, optional_param: str = None) -> bool:
    """Short description of what the method does.
    
    Longer description with more details if needed.
    
    Args:
        param: Description of param
        optional_param: Description of optional parameter
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When this exception is raised
        
    Example:
        >>> calendar = CalendarBase("alice")
        >>> calendar.method_name(10, "test")
        True
    """
```

#### README Updates

When adding new features, update:

- Feature list
- Quick start examples
- API reference
- Advanced examples (if applicable)

### 7. Performance Considerations

#### Core Requirements

- **Insertion**: O(log N)
- **Deletion**: O(log N)  
- **Search**: O(log N)
- **Range queries**: O(log N + k) where k is result size

#### Benchmark New Features

```python
# Add benchmarks for new functionality
def benchmark_new_feature():
    """Benchmark new feature performance."""
    runner = BenchmarkRunner()
    
    def test_function():
        # Implementation
        pass
    
    runner.run_benchmark("New Feature", test_function, iterations=100)
    return runner
```

## Release Process

1. **Update version** in `pyproject.toml` and `__init__.py`
2. **Update CHANGELOG.md** with new features and fixes
3. **Run full test suite** and benchmarks
4. **Create release PR** with version bump
5. **Tag release** after PR merge
6. **GitHub Actions** handles PyPI publishing

## Questions and Support

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Email**: For security issues or private inquiries

## License

By contributing to TimeSlotAssigner, you agree that your contributions will be licensed under the MIT License.
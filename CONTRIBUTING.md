# Contributing to Adventure Game

First off, thank you for considering contributing to Adventure Game! It's people like you that make this project better.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.7 or higher
- MySQL 5.7 or higher
- Git
- Basic understanding of Python and SQL

### First Contribution

Unsure where to begin? You can start by looking through these issues:

- **Beginner issues** - Issues labeled `good first issue`
- **Help wanted issues** - Issues labeled `help wanted`

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

When creating a bug report, include:

- **Clear title** - Descriptive and specific
- **Description** - Detailed explanation of the issue
- **Steps to reproduce** - Numbered list of steps
- **Expected behavior** - What should happen
- **Actual behavior** - What actually happens
- **Screenshots** - If applicable
- **Environment** - OS, Python version, MySQL version
- **Logs** - Relevant log entries from `adventure_game.log`

Example:
```markdown
**Title:** Combat system crashes when using Strength Potion

**Description:**
The game crashes when attempting to use a Strength Potion during combat.

**Steps to Reproduce:**
1. Start a new game
2. Enter combat with any enemy
3. Select "Use Item"
4. Select "Strength Potion"
5. Game crashes

**Expected Behavior:**
Strength buff should be applied and combat continues.

**Actual Behavior:**
Game crashes with AttributeError.

**Environment:**
- OS: Windows 10
- Python: 3.9.5
- MySQL: 8.0.25

**Logs:**
```
[ERROR] AttributeError: 'Player' object has no attribute 'status_effect_manager'
```
```

### Suggesting Features

Feature suggestions are welcome! Please provide:

- **Clear title** - Descriptive feature name
- **Problem statement** - What problem does this solve?
- **Proposed solution** - How should it work?
- **Alternatives** - Other solutions you've considered
- **Additional context** - Screenshots, mockups, examples

Example:
```markdown
**Title:** Add crafting system

**Problem:**
Players have limited ways to obtain powerful items.

**Proposed Solution:**
Add a crafting system where players can combine materials to create items.

**How It Works:**
1. Collect materials from enemies and locations
2. Access crafting menu from village
3. Select recipe and required materials
4. Craft item if materials are available

**Alternatives:**
- Enhanced shop with more items
- Random legendary drops

**Additional Context:**
Similar to crafting in Minecraft or Terraria.
```

### Code Contributions

1. **Fork the repository**
2. **Create a branch** - `git checkout -b feature/AmazingFeature`
3. **Make your changes**
4. **Add tests** - Ensure new features are tested
5. **Run tests** - All tests must pass
6. **Commit** - `git commit -m 'Add AmazingFeature'`
7. **Push** - `git push origin feature/AmazingFeature`
8. **Open Pull Request**

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/Vortex4047/adventure-game-text-based-.git
cd adventure-game-text-based-
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Database

```bash
# Start MySQL
# Configure credentials in config.py or use environment variables
export DB_PASSWORD=your_password
```

### 5. Run Tests

```bash
# Quick test
python test_game.py

# Full test suite
python -m unittest discover tests -v
```

### 6. Make Changes

```bash
# Create a new branch
git checkout -b feature/my-feature

# Make your changes
# ...

# Test your changes
python test_game.py
python -m unittest discover tests

# Commit
git add .
git commit -m "Add my feature"
```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line length**: 100 characters (not 79)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings
- **Imports**: Grouped and sorted

### Type Hints

All functions must include type hints:

```python
def calculate_damage(attacker_attack: int, defender_defense: int) -> int:
    """Calculate damage dealt in combat"""
    return max(1, attacker_attack - defender_defense)
```

### Docstrings

All functions and classes must have docstrings:

```python
def my_function(param1: str, param2: int) -> bool:
    """
    Brief description of what the function does.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param2 is negative
    """
    pass
```

### Logging

Use logging instead of print for debugging:

```python
import logging
logger = logging.getLogger(__name__)

# Good
logger.info(f"Player {name} dealt {damage} damage")
logger.error(f"Database error: {e}")

# Avoid
print(f"Debug: {value}")
```

### Error Handling

Always handle errors gracefully:

```python
try:
    result = risky_operation()
    logger.info("Operation successful")
    return result
except SpecificError as e:
    logger.error(f"Error: {e}")
    print("❌ User-friendly error message")
    return default_value
```

### Constants

Use constants from `constants.py`:

```python
# Good
from constants import CRIT_CHANCE_PLAYER
if random.random() < CRIT_CHANCE_PLAYER:
    damage *= 2

# Avoid
if random.random() < 0.15:  # Magic number
    damage *= 2
```

## Testing Guidelines

### Writing Tests

All new features must include tests:

```python
import unittest
from player import Player

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.player = Player("TestHero")
    
    def test_feature_works(self):
        """Test that feature works correctly"""
        result = self.player.new_feature()
        self.assertEqual(result, expected_value)
    
    def test_feature_handles_errors(self):
        """Test error handling"""
        with self.assertRaises(ValueError):
            self.player.new_feature(invalid_input)
```

### Running Tests

```bash
# Quick test
python test_game.py

# Specific test file
python -m unittest tests.test_player

# Specific test
python -m unittest tests.test_player.TestPlayer.test_feature

# All tests with verbose output
python -m unittest discover tests -v
```

### Test Coverage

Aim for at least 70% coverage for new code:

```bash
# Install coverage
pip install coverage

# Run with coverage
coverage run -m unittest discover tests
coverage report
coverage html  # Generate HTML report
```

## Pull Request Process

### Before Submitting

1. **Update documentation** - README, docstrings, etc.
2. **Add tests** - All new features must be tested
3. **Run tests** - All tests must pass
4. **Check code style** - Follow coding standards
5. **Update CHANGELOG.md** - Add your changes

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All tests pass
- [ ] Added new tests
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests added/updated
- [ ] CHANGELOG.md updated
```

### Review Process

1. **Automated checks** - Tests must pass
2. **Code review** - Maintainer reviews code
3. **Feedback** - Address any comments
4. **Approval** - Maintainer approves PR
5. **Merge** - PR is merged to main branch

### After Merge

- Your contribution will be credited
- Changes will be included in next release
- Thank you for contributing! 🎉

## Questions?

Feel free to ask questions by:

- Opening an issue with the `question` label
- Starting a discussion in GitHub Discussions
- Contacting the maintainers

## Recognition

Contributors will be recognized in:

- README.md contributors section
- Release notes
- CHANGELOG.md

Thank you for contributing to Adventure Game! 🗡️🛡️

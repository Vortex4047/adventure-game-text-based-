# 🚀 Quick Reference Card

## Repository Information
- **URL**: https://github.com/Vortex4047/adventure-game-text-based-
- **Version**: v2.0.0
- **License**: MIT

---

## Quick Commands

### Deploy to GitHub
```bash
# Windows
setup_git.bat

# Linux/Mac
chmod +x setup_git.sh && ./setup_git.sh
```

### Run the Game
```bash
python main.py
```

### Run Tests
```bash
# Quick test
python test_game.py

# Full tests
python -m unittest discover tests -v
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Project Structure

```
adventure-game-text-based-/
├── 🎮 Core (7 files)
│   ├── main.py
│   ├── player.py
│   ├── combat.py
│   ├── locations.py
│   ├── shop.py
│   ├── database.py
│   └── utils.py
│
├── ⚙️ Config (2 files)
│   ├── constants.py
│   └── config.py
│
├── ✨ Features (5 files)
│   ├── status_effects.py
│   ├── achievements.py
│   ├── random_events.py
│   ├── item_system.py
│   └── colors.py
│
├── 🧪 Tests (4 files)
│   ├── test_game.py
│   └── tests/
│
├── 📚 Docs (11 files)
│   ├── README.md
│   ├── QUICKSTART.md
│   ├── DEPLOYMENT.md
│   └── ...
│
└── 🔧 GitHub (8 files)
    ├── .github/
    ├── LICENSE
    └── .gitignore
```

---

## Key Features

| Feature | Count | Status |
|---------|-------|--------|
| Python Files | 19 | ✅ |
| Unit Tests | 28 | ✅ |
| Type Coverage | 95% | ✅ |
| Test Coverage | 70% | ✅ |
| Achievements | 17 | ✅ |
| Status Effects | 4 | ✅ |
| Random Events | 7 | ✅ |
| Item Rarities | 5 | ✅ |

---

## Important Links

### Repository
- **Main**: https://github.com/Vortex4047/adventure-game-text-based-
- **Issues**: https://github.com/Vortex4047/adventure-game-text-based-/issues
- **Actions**: https://github.com/Vortex4047/adventure-game-text-based-/actions

### Documentation
- [README](README.md) - Main documentation
- [Quick Start](QUICKSTART.md) - Getting started
- [Deployment](DEPLOYMENT.md) - Deploy to GitHub
- [Contributing](CONTRIBUTING.md) - How to contribute

---

## Common Tasks

### Create New Feature
```bash
git checkout -b feature/my-feature
# Make changes
python test_game.py
git add .
git commit -m "Add my feature"
git push origin feature/my-feature
```

### Fix Bug
```bash
git checkout -b fix/bug-name
# Fix bug
python -m unittest discover tests
git add .
git commit -m "Fix bug-name"
git push origin fix/bug-name
```

### Update Documentation
```bash
# Edit documentation files
git add *.md
git commit -m "Update documentation"
git push origin main
```

---

## Troubleshooting

### Database Error
```bash
# Check MySQL is running
# Update credentials in config.py
export DB_PASSWORD=your_password
```

### Import Error
```bash
pip install -r requirements.txt
```

### Test Failures
```bash
python test_game.py
# Check output for specific errors
```

---

## Contact & Support

- 🐛 **Report Bugs**: [Open an issue](https://github.com/Vortex4047/adventure-game-text-based-/issues)
- 💡 **Request Features**: [Open an issue](https://github.com/Vortex4047/adventure-game-text-based-/issues)
- 💬 **Ask Questions**: [Start a discussion](https://github.com/Vortex4047/adventure-game-text-based-/discussions)

---

## Quick Stats

```
📊 Project Statistics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Files:         44+
Lines of Code:       ~2,600
Documentation:       ~2,500 lines
Type Coverage:       95%
Test Coverage:       70%
Tests Passing:       28/28 ✅
```

---

**Version**: 2.0.0 | **Status**: Production Ready ✅ | **License**: MIT

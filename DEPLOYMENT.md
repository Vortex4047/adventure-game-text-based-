# 🚀 Deployment Guide

## Quick Deploy to GitHub

### Option 1: Using Setup Script (Recommended)

#### Windows
```bash
setup_git.bat
```

#### Linux/Mac
```bash
chmod +x setup_git.sh
./setup_git.sh
```

### Option 2: Manual Setup

```bash
# 1. Initialize git
git init

# 2. Add all files
git add .

# 3. Create initial commit
git commit -m "Initial commit - Adventure Game v2.0"

# 4. Add remote
git remote add origin https://github.com/Vortex4047/adventure-game-text-based-.git

# 5. Create main branch
git branch -M main

# 6. Push to GitHub
git push -u origin main

# 7. Create release tag
git tag -a v2.0.0 -m "Release v2.0.0 - Enhanced Edition"
git push origin v2.0.0
```

---

## Post-Deployment Steps

### 1. Configure Repository Settings

Visit: https://github.com/Vortex4047/adventure-game-text-based-/settings

#### General
- **Description**: "A professional-grade text-based RPG with combat, quests, achievements, status effects, and more! Built with Python."
- **Website**: Link to documentation or demo (optional)
- **Topics**: Add these tags:
  - `python`
  - `game`
  - `rpg`
  - `text-based`
  - `adventure`
  - `mysql`
  - `terminal`
  - `cli-game`
  - `turn-based`
  - `achievements`

#### Features
- ✅ Issues
- ✅ Projects (optional)
- ✅ Wiki (optional)
- ✅ Discussions (recommended)

### 2. Create Release

1. Go to: https://github.com/Vortex4047/adventure-game-text-based-/releases
2. Click "Create a new release"
3. Choose tag: `v2.0.0`
4. Release title: `v2.0.0 - Enhanced Edition`
5. Description: Copy from CHANGELOG.md
6. Click "Publish release"

### 3. Enable GitHub Actions

1. Go to: https://github.com/Vortex4047/adventure-game-text-based-/actions
2. Click "I understand my workflows, go ahead and enable them"
3. Workflows will run automatically on push and PR

### 4. Update README Badges

The badges in README.md will automatically work once the repository is public and Actions are enabled.

### 5. Add Social Preview (Optional)

1. Go to Settings
2. Scroll to "Social preview"
3. Upload an image (1280x640px recommended)
4. Suggested image: Game logo or screenshot

---

## Repository Structure

```
https://github.com/Vortex4047/adventure-game-text-based-
├── Code (19 Python files)
├── Tests (4 test files)
├── Documentation (11 guides)
├── GitHub Config (.github/)
└── Setup Scripts
```

---

## Verification Checklist

After deployment, verify:

- [ ] Repository is accessible
- [ ] README displays correctly
- [ ] All files are present
- [ ] GitHub Actions workflow runs
- [ ] Issues and PRs are enabled
- [ ] License is visible
- [ ] Topics are added
- [ ] Description is set

---

## Sharing Your Project

### Social Media

**Twitter/X:**
```
🎮 Just released Adventure Game v2.0! 

A professional text-based RPG with:
✨ 17 achievements
⚔️ Status effects
🎲 Random events
🎨 Color output
🧪 70% test coverage

Built with Python & MySQL

Check it out: https://github.com/Vortex4047/adventure-game-text-based-

#Python #GameDev #OpenSource
```

**Reddit:**
- r/Python
- r/gamedev
- r/learnprogramming
- r/opensource

**Dev.to:**
Create a post about the development process and features.

### Show HN

Post on Hacker News with title:
```
Show HN: Adventure Game – A professional text-based RPG in Python
```

---

## Maintenance

### Regular Tasks

1. **Monitor Issues**
   - Respond within 24-48 hours
   - Label appropriately
   - Close resolved issues

2. **Review Pull Requests**
   - Check tests pass
   - Review code quality
   - Provide feedback
   - Merge when ready

3. **Update Dependencies**
   ```bash
   pip list --outdated
   pip install --upgrade <package>
   ```

4. **Create Releases**
   - Update CHANGELOG.md
   - Bump version numbers
   - Create git tag
   - Publish release

### Release Process

```bash
# 1. Update version
# Edit constants.py: SAVE_FILE_VERSION = "2.1"

# 2. Update CHANGELOG.md
# Add new version section

# 3. Commit changes
git add .
git commit -m "Bump version to 2.1.0"

# 4. Create tag
git tag -a v2.1.0 -m "Release v2.1.0"

# 5. Push
git push origin main
git push origin v2.1.0

# 6. Create release on GitHub
```

---

## Troubleshooting

### Push Rejected

```bash
# If push is rejected, pull first
git pull origin main --rebase
git push origin main
```

### Authentication Issues

```bash
# Use personal access token
# Generate at: https://github.com/settings/tokens
# Use token as password when prompted
```

### Large Files

```bash
# If files are too large, add to .gitignore
echo "large_file.db" >> .gitignore
git rm --cached large_file.db
git commit -m "Remove large file"
```

---

## Support

### Getting Help

- 📖 [GitHub Docs](https://docs.github.com)
- 💬 [GitHub Community](https://github.community)
- 📚 [Git Documentation](https://git-scm.com/doc)

### Project Links

- **Repository**: https://github.com/Vortex4047/adventure-game-text-based-
- **Issues**: https://github.com/Vortex4047/adventure-game-text-based-/issues
- **Discussions**: https://github.com/Vortex4047/adventure-game-text-based-/discussions
- **Actions**: https://github.com/Vortex4047/adventure-game-text-based-/actions

---

## Success! 🎉

Your project is now live on GitHub and ready to share with the world!

**Repository URL:**
https://github.com/Vortex4047/adventure-game-text-based-

**Next Steps:**
1. Share on social media
2. Add to your portfolio
3. Invite contributors
4. Keep improving!

---

**Made with ❤️ and Python**

@echo off
REM Adventure Game - Git Setup Script (Windows)
REM This script initializes the git repository and pushes to GitHub

echo =========================================
echo   Adventure Game - Git Setup
echo =========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo X Git is not installed. Please install git first.
    pause
    exit /b 1
)

echo √ Git is installed
echo.

REM Initialize git repository
echo Initializing git repository...
git init

REM Add all files
echo Adding all files...
git add .

REM Create initial commit
echo Creating initial commit...
git commit -m "Initial commit - Adventure Game v2.0" -m "- Complete game implementation with 19 Python files" -m "- Type hints throughout (95%% coverage)" -m "- Comprehensive logging system" -m "- Status effects (4 types)" -m "- Achievement system (17 achievements)" -m "- Random events (7 types)" -m "- Color output system" -m "- Item rarity system (5 levels)" -m "- Unit tests (28 tests, 70%% coverage)" -m "- Complete documentation (11 guides)" -m "- GitHub-ready configuration"

REM Add remote
echo Adding remote repository...
git remote add origin https://github.com/Vortex4047/adventure-game-text-based-.git

REM Create main branch
echo Creating main branch...
git branch -M main

REM Push to GitHub
echo Pushing to GitHub...
git push -u origin main

REM Create and push tag
echo Creating release tag...
git tag -a v2.0.0 -m "Release v2.0.0 - Enhanced Edition"
git push origin v2.0.0

echo.
echo =========================================
echo   √ Setup Complete!
echo =========================================
echo.
echo Your repository is now on GitHub!
echo https://github.com/Vortex4047/adventure-game-text-based-
echo.
echo Next steps:
echo 1. Visit your repository on GitHub
echo 2. Create a release from tag v2.0.0
echo 3. Add repository description and topics
echo 4. Enable GitHub Actions
echo 5. Enable Discussions (optional)
echo.
echo Ready to share with the world!
echo.
pause

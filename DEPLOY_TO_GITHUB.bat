@echo off
echo ========================================
echo  GitHub Upload Script
echo ========================================
echo.

REM Change to project directory
cd /d C:\Users\ANIL777\OneDrive\Desktop\honeypot

echo Step 1: Adding all files to git...
git add .

echo.
echo Step 2: Committing files...
git commit -m "Complete honeypot system with advanced security features"

echo.
echo Step 3: Setting main branch...
git branch -M main

echo.
echo ========================================
echo  IMPORTANT: Update GitHub URL
echo ========================================
echo.
echo Before running the next command, you need to:
echo 1. Go to https://github.com/new
echo 2. Create repository named: honeypot-ecommerce
echo 3. Copy your GitHub username
echo.
echo Then run this command (replace YOUR_USERNAME):
echo.
echo git remote add origin https://github.com/YOUR_USERNAME/honeypot-ecommerce.git
echo git push -u origin main
echo.
echo ========================================
pause

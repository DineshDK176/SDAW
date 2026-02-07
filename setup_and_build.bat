@echo off
echo ==========================================
echo Setting up SDAW - Desktop Assistant Build
echo ==========================================
echo.
echo Installing requirements...
pip install -r requirements_modern.txt

echo.
echo Building Executable...
python build_script.py

echo.
echo ==========================================
echo Build Complete!
echo You can find 'SDAW_Assistant.exe' in the 'dist' folder.
echo ==========================================
pause

@echo off
echo Запуск сервера ПВЗ...
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Python не найден. Установите Python с python.org
    pause
    exit /b 1
)

REM Запуск сервера
python server.py

pause
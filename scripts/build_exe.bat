@echo off
title Multi-Parameter Data Analyzer - Build Script v1.1
echo.
echo =========================================================
echo   Multi-Parameter Data Analyzer v1.1 - Build Script
echo   Автоматическая сборка exe файла
echo =========================================================
echo.

REM Проверяем существование виртуальной среды
if not exist "venv_build\Scripts\activate.bat" (
    echo ОШИБКА: Виртуальная среда не найдена!
    echo Создаем новую виртуальную среду...
    python -m venv venv_build
    echo Виртуальная среда создана.
)

echo Активируем виртуальную среду...
call venv_build\Scripts\activate.bat

echo.
echo Обновляем pip...
python -m pip install --upgrade pip

echo.
echo Устанавливаем/обновляем зависимости...
pip install --upgrade -r requirements.txt

echo.
echo Устанавливаем/обновляем PyInstaller...
pip install --upgrade pyinstaller

echo.
echo Очищаем предыдущие сборки...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

echo.
echo Запускаем сборку exe файла...
echo Это может занять несколько минут...
pyinstaller graf_csv.spec --clean

echo.
echo Проверяем результат сборки...
if exist "dist\Multi-Parameter_Data_Analyzer.exe" (
    echo.
    echo =========================================================
    echo   ✅ СБОРКА ЗАВЕРШЕНА УСПЕШНО!
    echo =========================================================
    echo.
    echo Созданные файлы:
    dir /b "dist"
    echo.
    echo Размер exe файла:
    for %%F in ("dist\Multi-Parameter_Data_Analyzer.exe") do echo %%~zF байт
    echo.
    echo Файлы находятся в папке: dist\
    echo.
) else (
    echo.
    echo =========================================================
    echo   ❌ ОШИБКА СБОРКИ!
    echo =========================================================
    echo.
    echo Проверьте логи выше для диагностики проблемы.
    echo.
)

echo Нажмите любую клавишу для завершения...
pause >nul

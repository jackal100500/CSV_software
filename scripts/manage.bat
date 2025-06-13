@echo off
title Multi-Parameter Data Analyzer - Меню управления
:menu
cls
echo.
echo =========================================================
echo   Multi-Parameter Data Analyzer v1.1 - Меню управления
echo =========================================================
echo.
echo Выберите действие:
echo.
echo [1] Запустить приложение
echo [2] Пересобрать exe файл
echo [3] Открыть папку с exe файлом
echo [4] Показать информацию о сборке
echo [5] Открыть GitHub репозиторий
echo [0] Выход
echo.
set /p choice="Введите номер (0-5): "

if "%choice%"=="1" goto run_app
if "%choice%"=="2" goto build_app
if "%choice%"=="3" goto open_dist
if "%choice%"=="4" goto show_info
if "%choice%"=="5" goto open_github
if "%choice%"=="0" goto exit
goto menu

:run_app
echo.
echo Запуск приложения...
if exist "dist\Multi-Parameter_Data_Analyzer.exe" (
    start "" "dist\Multi-Parameter_Data_Analyzer.exe"
    echo Приложение запущено!
) else (
    echo ОШИБКА: exe файл не найден! Сначала выполните сборку (пункт 2).
)
echo.
pause
goto menu

:build_app
echo.
echo Запуск сборки...
call build_exe.bat
echo.
pause
goto menu

:open_dist
echo.
echo Открытие папки с файлами...
if exist "dist" (
    explorer "dist"
) else (
    echo ОШИБКА: Папка dist не найдена! Сначала выполните сборку.
)
echo.
pause
goto menu

:show_info
cls
echo.
echo =========================================================
echo   Информация о проекте
echo =========================================================
echo.
if exist "dist\Multi-Parameter_Data_Analyzer.exe" (
    echo ✅ Приложение собрано
    echo.
    echo Файлы в dist:
    dir /b "dist" 2>nul
    echo.
    for %%F in ("dist\Multi-Parameter_Data_Analyzer.exe") do (
        echo Размер exe: %%~zF байт
        echo Дата создания: %%~tF
    )
) else (
    echo ❌ Приложение не собрано
    echo Используйте пункт 2 для сборки.
)
echo.
echo Версия: 1.1
echo Разработчик: j15
echo GitHub: https://github.com/jackal100500/CSV_software.git
echo.
pause
goto menu

:open_github
echo.
echo Открытие GitHub репозитория...
start "" "https://github.com/jackal100500/CSV_software.git"
echo.
pause
goto menu

:exit
echo.
echo До свидания!
echo.
timeout /t 2 /nobreak >nul
exit

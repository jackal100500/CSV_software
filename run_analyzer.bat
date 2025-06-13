@echo off
title Multi-Parameter Data Analyzer v1.1
echo.
echo =====================================================
echo   Multi-Parameter Data Analyzer v1.1
echo   Запуск приложения...
echo =====================================================
echo.

REM Проверяем существование exe файла
if not exist "dist\Multi-Parameter_Data_Analyzer.exe" (
    echo ОШИБКА: Исполняемый файл не найден!
    echo Убедитесь, что файл dist\Multi-Parameter_Data_Analyzer.exe существует.
    pause
    exit /b 1
)

REM Запускаем приложение
echo Запуск Multi-Parameter Data Analyzer...
start "" "dist\Multi-Parameter_Data_Analyzer.exe"

echo.
echo Приложение запущено!
echo Если возникли проблемы, проверьте логи или обратитесь к разработчику.
echo.
echo GitHub: https://github.com/jackal100500/CSV_software.git
echo.
timeout /t 3 /nobreak >nul

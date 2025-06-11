@echo off
echo =========================================
echo  Multi-Parameter Analyzer - EXE Builder
echo =========================================
echo.

echo 🔧 Создание виртуальной среды...
python -m venv venv_build

echo ✅ Активация виртуальной среды...
call venv_build\Scripts\activate.bat

echo 📦 Установка зависимостей для сборки...
python -m pip install --upgrade pip
pip install -r requirements_build.txt

echo 🧹 Очистка предыдущих сборок...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo 🚀 Создание EXE файла...
pyinstaller graf_csv.spec --clean --noconfirm

echo.
echo =========================================
if exist dist\MultiParameterAnalyzer.exe (
    echo ✅ СБОРКА ЗАВЕРШЕНА УСПЕШНО!
    echo 📁 Файл: dist\MultiParameterAnalyzer.exe
    
    echo 📊 Размер файла:
    for %%A in (dist\MultiParameterAnalyzer.exe) do echo    %%~zA байт
    
    echo.
    echo 🧪 Запустить тест? (y/n)
    set /p test_choice=
    if /i "%test_choice%"=="y" (
        echo 🚀 Запуск теста...
        start "" "dist\MultiParameterAnalyzer.exe"
    )
) else (
    echo ❌ ОШИБКА СБОРКИ!
    echo Проверьте лог выше для деталей.
)

echo.
echo 🧹 Деактивация виртуальной среды...
deactivate

echo.
echo 💡 Чтобы удалить виртуальную среду после сборки:
echo    rmdir /s /q venv_build
echo.
pause

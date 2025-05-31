@echo off
rem ─────────────────────────────────────────────────────────────
rem run_project.bat  –  старт Django-проекта в Windows-окружении
rem  usage:
rem      run_project.bat          ← обычный дев-запуск
rem      run_project.bat prod     ← + collectstatic
rem ─────────────────────────────────────────────────────────────

setlocal enabledelayedexpansion
cd /d %~dp0

rem 1) виртуальное окружение
set VENV=.venv
if not exist "%VENV%\Scripts\python.exe" (
    echo [info] Создаю виртуальное окружение...
    py -3 -m venv %VENV%
)

echo [info] Активирую виртуальное окружение...
call "%VENV%\Scripts\activate.bat"

rem 2) зависимости
echo [info] Устанавливаю зависимости...
if exist requirements.txt (
    pip install -r requirements.txt
) else (
    echo [warn] requirements.txt не найден – пропускаю установку пакетов.
)

rem 3) миграции
echo [info] Применяю migrations...
python manage.py migrate

rem 4) статика (только если указан аргумент prod)
if "%1"=="prod" (
    echo [info] Собираю static-файлы...
    python manage.py collectstatic --noinput
)

rem 5) запуск сервера
echo [info] Запускаю Django-сервер http://127.0.0.1:8000
python manage.py runserver

endlocal
pause

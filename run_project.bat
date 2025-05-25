@echo off
rem ────────────────────────────────────────────────────────────
rem  project_run.bat – быстрое поднятие портала под Windows
rem  1) создаёт/активирует venv (.venv)
rem  2) ставит зависимости (requirements.txt)
rem  3) применяет миграции
rem  4) запускает сервер  Django
rem ────────────────────────────────────────────────────────────

:: перейти в папку, где лежит bat-файл
pushd "%~dp0"

:: 1. виртуальное окружение
if not exist ".venv\Scripts\activate.bat" (
    echo === Создаю виртуальное окружение ===
    py -m venv .venv
)

call ".venv\Scripts\activate.bat"

:: 2. зависимости
if exist "requirements.txt" (
    echo === Устанавливаю зависимости ===
    pip install -r requirements.txt
)

:: 3. миграции
echo === Применяю миграции ===
python manage.py makemigrations
python manage.py migrate

:: 4. запуск сервера
echo === Старт сервера на http://127.0.0.1:8000/ ===
python manage.py runserver 0.0.0.0:8000

popd

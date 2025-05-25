# 🎓 Портал _«REU Student Portal»_

Веб-приложение студенческого совета ФФМ РЭУ им. Г. В. Плеханова  
(новости, мероприятия, расписание, личный кабинет).

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.2-success?logo=django)
![License](https://img.shields.io/badge/License-MIT-informational)

---

## ✨ Возможности

| Блок | Что умеет |
|------|-----------|
| **Главная** | ближайшие мероприятия, последние новости, встроенный Google Calendar |
| **Мероприятия** | роли _гость / участник / организатор_, запись одним кликом, экспорт в GCal |
| **Новости** | лента + детальная страница |
| **Расписание** | уроки вашей учебной группы (только после входа) |
| **Личный кабинет** | изменение профиля, пароля, список регистраций |
| **UI** | Bootstrap 5, бургер-меню, адаптив для телефона |
| **Соц-сети** | кнопки-ссылки → [Vk](https://vk.com/reusovet) • [Telegram](https://t.me/ffm_sovetreu) |
| **Админ** | /admin/ — полное управление моделями |

---

## 🗂 Технологический стек

* **Python 3.11** + **Django 5.2**
* Bootstrap 5 / Bootstrap-Icons
* SQLite по-умолчанию ⇢ PostgreSQL в проде
* Gunicorn + Nginx (инструкция ниже)  
  _или_ Docker-image (по желанию)

---

## ⚡ Быстрый старт локально

### Windows / macOS / Linux (ручной способ)

```bash
git clone https://github.com/your-nickname/student_portal.git
cd student_portal

python -m venv .venv
# Windows: .\.venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

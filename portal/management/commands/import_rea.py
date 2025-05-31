"""
Импорт новостей и мероприятий с сайта rea.ru
Запуск:
    python manage.py import_rea [--news 10] [--events 10] [--clear]
"""

from __future__ import annotations

import datetime as dt
import re
import time
from typing import Iterable

import requests
from bs4 import BeautifulSoup, Tag
from django.core.management.base import BaseCommand
from django.utils import timezone
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from portal.models import News, Event

# ───────────────────  Session с ретраями и заголовками ───────────────────
SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml",
    }
)
retries = Retry(
    total=3,
    backoff_factor=1.5,
    status_forcelist=[429, 500, 502, 503, 504],
)
SESSION.mount("https://", HTTPAdapter(max_retries=retries))
SESSION.mount("http://", HTTPAdapter(max_retries=retries))

# ───────────────────  Словарь месяцев для RU → int ───────────────────────
MONTHS_RU = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}


# ───────────────────────────  Вспомогательные функции ────────────────────
def fetch(url: str) -> BeautifulSoup:
    """GET c 60-секундным тайм-аутом и ретраями. При неудаче → пустой BS."""
    try:
        resp = SESSION.get(url, timeout=60)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "lxml")
    except requests.RequestException as e:
        print(f"[warn] не смог загрузить {url}: {e}")
        return BeautifulSoup("", "lxml")


def is_trash(text: str) -> bool:
    """Фильтруем сервисные абзацы («задать вопрос», пустые строки»)."""
    t = text.lower()
    return (
        not t
        or "задать" in t
        and "вопрос" in t
        or "заполнив поля" in t
    )


# ─────────────────────────────  Парсер rea.ru  ────────────────────────────
class ReaParser:
    NEWS_URL = "https://www.rea.ru/news"
    EVENTS_URL = "https://www.rea.ru/events"

    # ─────────────────────────── Новости ────────────────────────────────
    def parse_news(self, limit: int = 10) -> Iterable[dict]:
        soup = fetch(self.NEWS_URL)
        links = soup.select('a[href^="/news/"]')
        seen, news = set(), []

        for a in links:
            href = a["href"]
            title = a.get_text(" ", strip=True)
            if not title or title in seen:
                continue
            seen.add(title)
            full_url = f"https://www.rea.ru{href}"

            art = fetch(full_url)
            article_node = (
                art.select_one("div.article__body")
                or art.select_one("div.news-detail__text")
                or art.select_one("article")
                or art
            )

            # прямые дочерние p, h2, h3, img
            elems = [
                el
                for el in article_node.children
                if isinstance(el, Tag) and el.name in ("p", "h2", "h3", "img")
            ]

            good = []
            for el in elems:
                txt = el.get_text(strip=True) if el.name != "img" else ""
                if is_trash(txt):
                    continue
                good.append(str(el))
                if len(good) == 3:
                    break

            body_html = "".join(good)

            # дата
            date_node = art.select_one(".article__date, .news-detail__date")
            date_str = date_node.get_text(strip=True) if date_node else ""
            m = re.search(r"(\d{1,2})\s+([а-яё]+)(?:\s+(\d{4}))?", date_str, re.I)
            if m:
                d, mon_ru, y = int(m[1]), m[2].lower(), m[3]
                year = int(y) if y else timezone.now().year
                month = MONTHS_RU.get(mon_ru, 1)
                published = dt.datetime(year, month, d, tzinfo=timezone.get_default_timezone())
            else:
                published = timezone.now()

            news.append(
                {
                    "title": title,
                    "body": body_html + f"<p><a href='{full_url}' target='_blank'>Читать на rea.ru</a></p>",
                    "published": published,
                }
            )
            if len(news) >= limit:
                break
        return news

    # ────────────────────────── Мероприятия ─────────────────────────────
    # ─────────────────────── EVENTS  ───────────────────────────
    def parse_events(self, limit: int = 10) -> Iterable[dict]:
        """
        Список ссылок /event/… или /events/…  → детальная страница.
        Берём первые 2-3 «чистых» абзаца, дату, формируем описание.
        """
        soup = fetch(self.EVENTS_URL)
        links = soup.select('a[href^="/event/"], a[href^="/events/"]')
        print(f"[debug] найдено ссылок мероприятий: {len(links)}")

        seen, events = set(), []

        for a in links:
            href = a["href"]
            title = a.get_text(" ", strip=True)
            if not title or title in seen:
                continue
            seen.add(title)
            full_url = f"https://www.rea.ru{href}"

            # ── детальная страница ─────────────────────────────
            art = fetch(full_url)
            node = (
                    art.select_one("div.event-detail__text")
                    or art.select_one("div.article__body")
                    or art.select_one("article")
                    or art
            )

            # прямые дети p/h2/h3/img
            elems = [
                el for el in node.children
                if isinstance(el, Tag) and el.name in ("p", "h2", "h3", "img")
            ]

            good = []
            for el in elems:
                txt = el.get_text(strip=True) if el.name != "img" else ""
                if is_trash(txt):
                    continue
                good.append(str(el))
                if len(good) == 3:
                    break

            body_html = "".join(good)

            # ── дата ───────────────────────────────────────────
            date_node = art.select_one(".event-detail__date, .article__date")
            date_txt = date_node.get_text(" ", strip=True) if date_node else title
            m = re.search(r"(\d{1,2})\s+([а-яё]+)(?:\s+(\d{4}))?", date_txt, re.I)
            if not m:
                print(f"[warn] пропускаю без даты: {full_url}")
                continue
            d, mon_ru, y = int(m[1]), m[2].lower(), m[3]
            year = int(y) if y else timezone.now().year
            month = MONTHS_RU.get(mon_ru, 1)

            try:
                start = dt.datetime(year, month, d,
                                    tzinfo=timezone.get_default_timezone())
            except ValueError:
                print(f"[warn] пропускаю событие с неверной датой: {date_txt} ({full_url})")
                continue

            events.append(
                {
                    "title": title,
                    "description": body_html + f"<p><a href='{full_url}' target='_blank'>Смотреть на rea.ru</a></p>",
                    "start_time": start,
                    "end_time": None,
                }
            )
            if len(events) >= limit:
                break

            time.sleep(0.7)  # пауза, чтобы не «ударить» по серверу
        return events


# ──────────────────────────────  Django command  ───────────────────────────
class Command(BaseCommand):
    help = "Импорт новостей и/или мероприятий с сайта rea.ru"

    def add_arguments(self, parser):
        parser.add_argument("--news", type=int, default=10, help="Сколько новостей брать")
        parser.add_argument("--events", type=int, default=10, help="Сколько мероприятий брать")
        parser.add_argument("--clear", action="store_true", help="Очистить импортированные записи перед загрузкой")

    def handle(self, *args, **opts):
        print("- Проверяю доступность https://www.rea.ru/news ...")
        test = SESSION.get("https://www.rea.ru/news", timeout=30)
        print(f"  status={test.status_code}, len={len(test.text)}")

        if opts["clear"]:
            self.stdout.write("- Удаляем прежние импортированные записи…")
            News.objects.filter(body__contains="rea.ru").delete()
            Event.objects.filter(description__contains="rea.ru").delete()

        parser = ReaParser()
        imported_news = 0
        imported_events = 0

        # ----------- новости -----------
        for data in parser.parse_news(opts["news"]):
            obj, created = News.objects.get_or_create(title=data["title"], defaults=data)
            if created:
                imported_news += 1

        # --------- мероприятия ----------
        for data in parser.parse_events(opts["events"]):
            obj, created = Event.objects.get_or_create(title=data["title"], defaults=data)
            if created:
                imported_events += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Импорт завершён: новостей добавлено {imported_news}, мероприятий добавлено {imported_events}."
            )
        )

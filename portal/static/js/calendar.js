document.addEventListener('DOMContentLoaded', async () => {
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;

    // получаем события через API (упрощённо – берём data-атрибут, можно сделать DRF endpoint)
    const events = JSON.parse(calendarEl.dataset.events || '[]');

    new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'ru',
        height: 450,
        events: events
    }).render();
});

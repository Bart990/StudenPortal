# portal/templatetags/form_extras.py
from django import template

register = template.Library()


@register.filter(name="add_class")
def add_class(field, css):
    """
    Добавляет CSS-класс к полю формы прямо в шаблоне.

        {{ form.username|add_class:"form-control" }}

    Возвращает HTML-строку, поэтому можно применять к BoundField.
    """
    # какие классы уже есть у виджета
    existing = field.field.widget.attrs.get("class", "")
    # объединяем и избавляемся от дублирования пробелов
    classes = f"{existing} {css}".strip()
    # возвращаем рендер виджета с обновлённым атрибутом
    return field.as_widget(
        attrs={**field.field.widget.attrs, "class": classes}
    )

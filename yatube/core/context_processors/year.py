from datetime import date


def year(reques):
    """Добавляет переменную с текущим годом."""
    return {'year': int(date.today().year)}

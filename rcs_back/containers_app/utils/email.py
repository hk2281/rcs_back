from rcs_back.containers_app.models import Container


def public_container_add_notify(container: Container) -> None:
    """Отправляет сообщение с инструкциями для активации
    добавленного контейнера"""
    pass


def send_public_feedback(email: str, msg: str, container_id: int = 0) -> None:
    """Отправляет сообщение с обратной связью на почту экологу"""
    pass

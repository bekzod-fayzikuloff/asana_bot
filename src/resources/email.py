DEFAULT_TEXT = "Вы забыли отметить меня!"
EXPIRED_TEXT = "Если да, то укажи в сроке выполнения текущую дату и напиши комментарий к данной задаче. Не забудь отметить в комментарии меня!"  # noqa


def make_story_hmtl(assigner: dict, placeholder: str):
    return f"""<body><a href="#" data-asana-gid="{assigner['gid']}" \
    data-asana-accessible="true" data-asana-type="user" \
    data-asana-dynamic="true">@{assigner['name']}</a> Задача выполнена? {placeholder}
    </body>"""

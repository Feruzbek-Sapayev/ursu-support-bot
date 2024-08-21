from aiogram import Router

from filters import ChatPrivateFilter


def setup_routers() -> Router:
    from .users import admin, start, help, echo, register, events, application
    from .errors import error_handler
    from .groups import group

    router = Router()

    # Agar kerak bo'lsa, o'z filteringizni o'rnating
    # start.router.message.filter(ChatPrivateFilter(chat_type=["private"]))

    router.include_routers(start.router, admin.router, group.router, register.router, application.router, events.router, help.router, echo.router, error_handler.router)

    return router

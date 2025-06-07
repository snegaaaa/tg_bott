from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Any, Dict
from database import get_db_session

class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        # Inject db session
        async for session in get_db_session():
            data["db_session"] = session
            return await handler(event, data)
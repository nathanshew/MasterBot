import os
from abc import ABC, abstractmethod


class BaseJob(ABC):

    @property
    @abstractmethod
    def text(self) -> str:
        pass

    async def send(self, context):
        chat_id = os.getenv("CHAT_ID")
        thread_id = os.getenv("THREAD_ID")
        await context.bot.send_message(
            chat_id=chat_id,
            text=self.text,
            **({"message_thread_id": thread_id} if thread_id else {})
        )

    @abstractmethod
    def register(self, app):
        pass

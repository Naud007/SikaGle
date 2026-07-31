from app.conversation.models.message import (
    Message,
)


class ConversationSummarizer:

    def summarize(
        self,
        messages: list[Message],
        max_messages: int = 10,
    ) -> str:

        recent = messages[-max_messages:]

        return "\n".join(
            f"{message.author}: {message.content}"
            for message in recent
        )

from app.conversation.models.message import (
    Message,
)


class ConversationPolicy:

    def should_ask_again(
        self,
        question: str,
        history: list[Message],
    ) -> bool:

        for message in history:

            if (
                message.author == "assistant"
                and message.content.strip().lower()
                == question.strip().lower()
            ):
                return False

        return True

    def should_end(
        self,
        history: list[Message],
    ) -> bool:

        if not history:
            return False

        last = history[-1].content.lower()

        endings = (
            "merci",
            "au revoir",
            "à bientôt",
            "bye",
        )

        return any(
            word in last
            for word in endings
        )

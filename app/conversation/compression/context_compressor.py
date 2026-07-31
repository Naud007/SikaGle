from app.conversation.compression.conversation_summarizer import (
    ConversationSummarizer,
)
from app.conversation.models.message import (
    Message,
)


class ContextCompressor:

    def __init__(self):

        self.summarizer = (
            ConversationSummarizer()
        )

    def compress(
        self,
        messages: list[Message],
    ) -> str:

        return self.summarizer.summarize(
            messages
        )

from app.conversation.state.conversation_state import (
    ConversationState,
)


class StateManager:

    def __init__(self):

        self._states: dict[
            str,
            ConversationState,
        ] = {}

    def get(
        self,
        user_id: str,
    ) -> ConversationState:

        return self._states.get(
            user_id,
            ConversationState.START,
        )

    def set(
        self,
        user_id: str,
        state: ConversationState,
    ) -> None:

        self._states[user_id] = state

    def reset(
        self,
        user_id: str,
    ) -> None:

        self._states[user_id] = (
            ConversationState.START
        )

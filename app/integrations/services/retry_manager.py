from datetime import datetime, timedelta
from uuid import uuid4

from app.integrations.models.retry_task import (
    RetryTask,
)


class RetryManager:

    def create_task(
        self,
        operation: str,
        payload: dict,
        max_attempts: int = 3,
        delay_seconds: int = 60,
    ) -> RetryTask:

        return RetryTask(
            task_id=str(uuid4()),
            operation=operation,
            payload=payload,
            attempts=0,
            max_attempts=max_attempts,
            next_retry_at=(
                datetime.utcnow()
                + timedelta(
                    seconds=delay_seconds
                )
            ),
        )

    def should_retry(
        self,
        task: RetryTask,
    ) -> bool:

        return (
            task.attempts
            < task.max_attempts
        )

    def register_attempt(
        self,
        task: RetryTask,
        delay_seconds: int = 60,
    ) -> RetryTask:

        task.attempts += 1

        task.next_retry_at = (
            datetime.utcnow()
            + timedelta(
                seconds=delay_seconds
            )
        )

        return task

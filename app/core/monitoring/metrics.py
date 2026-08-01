from datetime import datetime
from threading import Lock


class Metrics:

    def __init__(self):

        self.lock = Lock()

        self.started_at = datetime.utcnow()

        self.total_requests = 0

        self.total_errors = 0

        self.whatsapp_messages = 0

        self.rag_requests = 0

        self.llm_requests = 0

    def increment_requests(self):

        with self.lock:

            self.total_requests += 1

    def increment_errors(self):

        with self.lock:

            self.total_errors += 1

    def increment_whatsapp(self):

        with self.lock:

            self.whatsapp_messages += 1

    def increment_rag(self):

        with self.lock:

            self.rag_requests += 1

    def increment_llm(self):

        with self.lock:

            self.llm_requests += 1

    def snapshot(self):

        uptime = datetime.utcnow() - self.started_at

        return {

            "uptime_seconds": int(uptime.total_seconds()),

            "total_requests": self.total_requests,

            "total_errors": self.total_errors,

            "whatsapp_messages": self.whatsapp_messages,

            "rag_requests": self.rag_requests,

            "llm_requests": self.llm_requests

        }


metrics = Metrics()

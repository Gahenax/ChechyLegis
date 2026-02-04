import time
from typing import Dict, Any

class TechMetrics:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TechMetrics, cls).__new__(cls)
            cls._instance.start_time = time.time()
            cls._instance.request_count = 0
            cls._instance.error_count = 0
            cls._instance.ia_tokens_estimate = 0
            cls._instance.last_latency = 0.0
        return cls._instance

    def log_request(self, status_code: int, latency: float):
        self.request_count += 1
        if status_code >= 400:
            self.error_count += 1
        self.last_latency = latency

    def log_ia_usage(self, estimated_tokens: int):
        self.ia_tokens_estimate += estimated_tokens

    def get_report(self) -> Dict[str, Any]:
        uptime = time.time() - self.start_time
        return {
            "uptime_seconds": round(uptime, 2),
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": round(self.error_count / self.request_count, 4) if self.request_count > 0 else 0,
            "last_latency_seconds": round(self.last_latency, 4),
            "ia_tokens_estimated": self.ia_tokens_estimate,
            "status": "OPERATIONAL"
        }

metrics = TechMetrics()

def exponential_backoff(attempt: int, base_seconds: int = 60):
    return base_seconds * (2 ** max(attempt - 1, 0))

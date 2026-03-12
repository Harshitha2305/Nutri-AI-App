import time

class BaseAgent:
    def __init__(self, name, description=None, emoji=None):
        self.name = name
        self.description = description
        self.emoji = emoji

    def run(self, *args, **kwargs):
        raise NotImplementedError("Each agent must implement the run method.")

    def _timed_run(self, *args, **kwargs):
        start = time.time()
        result = self.run(*args, **kwargs)
        end = time.time()

        return {
            "result": result,
            "execution_time": round(end - start, 4),
            "agent": self.name
        }

    def status_line(self):
        return f"{self.emoji or '🤖'} {self.name}"
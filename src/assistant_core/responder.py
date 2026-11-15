from typing import Protocol

from assistant_core.models import Rule


class Responder(Protocol):
    def explain(self, question: str, rule: Rule) -> str:
        ...


class TemplateResponder:
    def explain(self, question: str, rule: Rule) -> str:
        return f"{rule.title}: {rule.text}"


'''class StubLLMResponder:
    def __init__(self, fail: bool = False):
        self.fail = fail

    def explain(self, question: str, rule: Rule) -> str:
        if self.fail:
            raise ProviderError("stub provider unavailable")
        return f"Based on '{rule.title}': {rule.text}"'''

# Task 20: Retired StubLLMResponder (kept alias temporarily until service/__main__/tests are rewired)
class StubLLMResponder(TemplateResponder):
    """Deprecated: retired in Lab 6 (kept stub wrapper until service/tests are rewired)."""

    def __init__(self, *args, **kwargs) -> None:
        pass
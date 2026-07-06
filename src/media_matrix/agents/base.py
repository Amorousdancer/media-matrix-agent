from abc import ABC, abstractmethod

from media_matrix.client import DeepSeekClient
from media_matrix.state import State


class BaseAgent(ABC):
    name: str

    def __init__(self, name: str | None = None) -> None:
        self.name = name or self.__class__.__name__
        self.llm_client = DeepSeekClient()

    def run(self, state: State) -> State:
        return self.process(state)

    @abstractmethod
    def process(self, state: State) -> State:
        """Update and return the workflow state."""

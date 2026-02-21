from abc import abstractmethod
from src.schemas.schemas import State
from src.utils.utils import get_llm


class BaseAgent:

    def __init__(self):
        self.llm = get_llm()

    @abstractmethod
    def generate_prompt(self) -> str:
        pass

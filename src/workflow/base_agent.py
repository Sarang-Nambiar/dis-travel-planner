from src.utils.utils import get_llm


class BaseAgent:

    def __init__(self):
        self.llm = get_llm()

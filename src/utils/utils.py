"""
Utilities file
"""
from config.settings import settings
from langchain_openai import ChatOpenAI

# TODO: Replace this with the langchain version for tracing with Langsmith
def get_llm(model='deepseek/deepseek-r1-0528:free'):
    llm = ChatOpenAI(base_url=settings.base_url, model=model, api_key=settings.auth_key)
    return llm

if __name__ == "__main__":
    # run_inference()
    pass

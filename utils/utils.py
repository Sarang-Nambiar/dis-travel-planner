"""
Utilities file
"""
from openai import OpenAI
from langchain.agents import create_agent
from config.settings import settings

# TODO: Replace this with the langchain version for tracing with Langsmith
def run_inference():
    client = OpenAI(
        base_url=settings.base_url,
        api_key=settings.auth_key.get_secret_value() 
    )

    completion = client.chat.completions.create(
    model="deepseek/deepseek-r1-0528:free",
    messages=[
        {
        "role": "user",
        "content": "What is the meaning of life?"
        }
    ]
    )
    response = completion.choices[0].message.content
    print(response)
    return response

if __name__ == "__main__":
    # run_inference()
    pass

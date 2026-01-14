from fastapi import FastAPI
from utils.utils import run_inference

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/plan")
async def get_travel_plan():
    """
    This is the service to invoke the planning process
    """

    # TODO: Invoke the travel planning agents.
    run_inference()

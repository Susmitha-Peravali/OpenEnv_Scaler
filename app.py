from fastapi import FastAPI
from env.openenv import OpenEnv

app = FastAPI()

@app.get("/")
def home():
    return {"status": "OpenEnv API running"}

@app.post("/reset")
def reset():
    env = OpenEnv()
    obs = env.reset()
    return {
        "task_type": obs.task_type,
        "content": obs.content
    }
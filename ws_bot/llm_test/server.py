from fastapi import FastAPI

app = FastAPI()

@app.get("/chat")
async def chat():
    return {"response": "Hello from the LLM server!"}

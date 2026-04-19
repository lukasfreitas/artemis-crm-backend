from fastapi import FastAPI

from app.api.routes import auth

app = FastAPI(title="Artemis API")
app.include_router(auth.router)

@app.get("/")
def root():
    return {"status": "ok"}
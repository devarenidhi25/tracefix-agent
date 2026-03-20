from fastapi import FastAPI
from app.routes.debug_route import router as debug_router

app = FastAPI(
    title="TraceFix Agent",
    description="AI debugging agent for analyzing and fixing programming errors",
    version="1.0.0"
)

app.include_router(debug_router)


@app.get("/")
def root():
    return {
        "message": "TraceFix Agent is running 🚀"
    }

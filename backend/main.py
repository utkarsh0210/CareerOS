from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import analyzer, tailor, network, interview, tracker

app = FastAPI(
    title="CareerOS API",
    description="AI-powered career assistant — MVP using Gemini 1.5 Flash (free tier)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyzer.router)
app.include_router(tailor.router)
app.include_router(network.router)
app.include_router(interview.router)
app.include_router(tracker.router)


@app.get("/health")
def health():
    return {"status": "ok", "model": "gemini-1.5-flash"}

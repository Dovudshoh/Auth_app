from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import auth, resources

app = FastAPI(
    title="Auth & RBAC Service",
    description="Custom authentication and role-based access control system",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(resources.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "Auth & RBAC Service"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}

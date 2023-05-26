import uvicorn
from fastapi import FastAPI

from auth.router import router as router_auth
from tasks.router import router as router_tasks

app = FastAPI(
    title='Todo'
)

app.include_router(router_auth)
app.include_router(router_tasks)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)

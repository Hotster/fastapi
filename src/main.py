import uvicorn
from fastapi import FastAPI

from auth.router import router as router_auth


app = FastAPI(
    title='Todo'
)


app.include_router(router_auth)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)

from fastapi import FastAPI

from auth.router import router as router_auth
from tasks.router import router as router_tasks
from users.router import router as router_users

app = FastAPI(
    title='Todo'
)

app.include_router(router_auth)
app.include_router(router_users)
app.include_router(router_tasks)

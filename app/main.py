from fastapi import FastAPI
from app.routers import goon_auth
from app.config import logging_settings
from app.logging_hook import setup_logging_hook

app = FastAPI(title="Awful Auth", description="Authentication for awful people")
app.include_router(goon_auth.router)

# Enable loguru and logging fastapi hooks
logging_settings.setup_loguru()
setup_logging_hook()

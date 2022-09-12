import logging
import uvicorn
from fastapi import FastAPI

from config import config
from routers import billing
from database.db import init_db

log = logging.getLogger(config.log.name)
app = FastAPI(title=config.app_name, version=config.version)


if __name__ == '__main__':
    app.include_router(billing.router)
    log_config = uvicorn.config.LOGGING_CONFIG
    del log_config["loggers"]["uvicorn"]  # Чтобы избежать двойного логирования
    log_config["formatters"]["default"]["fmt"] = config.log.format
    log_config["formatters"]["access"]["fmt"] = config.log.format
    init_db()
    uvicorn.run(app, log_config=log_config, host="0.0.0.0", port=config.port)

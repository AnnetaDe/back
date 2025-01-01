import os
import uvicorn
from app import app
from app.helpers.setup_logger import setup_logging


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    debug = os.environ.get("DEBUG", "False").lower() in ("true", "1", "t")
    setup_logging()
    uvicorn.run("app:app", port=port, reload=debug)

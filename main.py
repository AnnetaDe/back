import os
import uvicorn
from app import app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "False").lower() in ("true", "1", "t")
    uvicorn.run("app:app", port=port, reload=debug, host="0.0.0.0")

import os
import uvicorn
from app import app


def main():
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "False").lower() in {"true", "1", "t"}

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=debug,
        log_level="debug" if debug else "info",
    )


if __name__ == "__main__":
    main()

import os
import uvicorn


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("DEBUG", "False").lower() in ("true", "1", "t")
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=debug)
    print(port)

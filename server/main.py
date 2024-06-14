import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

from core.config import config

if __name__ == "__main__":
    uvicorn.run(
        app="core.server:app",
        reload=True if config.ENVIRONMENT != "production" else False,
        host=os.environ.get("SERVER_HOST", "0.0.0.0"),
        port=os.environ.get("SERVER_PORT", 8000),
        workers=1,
    )

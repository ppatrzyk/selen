import os
import uvicorn
from app import app

WORKERS = int(os.environ.get('WORKERS') or 1)
LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'info'

if __name__ == '__main__':
    uvicorn.run(
        'app.app:app',
        host="0.0.0.0",
        port=5000,
        log_level=LOG_LEVEL,
        workers=WORKERS
    )
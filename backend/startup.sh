#!/bin/startup.sh
cd /home/site/wwwroot/backend
pip install -r /home/site/wwwroot/backend/requirements.txt
uvicorn service:app --host 0.0.0.0 --port 8000
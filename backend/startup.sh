#!/bin/bash
cd /home/site/wwwroot/backend
pip install -r /home/site/wwwroot/requirements.txt
uvicorn service:app --host 0.0.0.0 --port 8000
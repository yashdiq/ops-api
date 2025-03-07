#!/bin/bash

# Run the application
uv run daphne -b 0.0.0.0 -p 8000 config.asgi:application
# uv run uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --workers 4
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY gemini_live_stream_client.py audio_video_multiplexer.py ./

ENV PYTHONUNBUFFERED=1
EXPOSE 9090

CMD ["python", "gemini_live_stream_client.py"]

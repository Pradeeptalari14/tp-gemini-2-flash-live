#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo " Validating Gemini 2.0 Flash Live API Gateway"
echo "=================================================="

python3 -m py_compile gemini_live_stream_client.py
python3 -m py_compile audio_video_multiplexer.py

python3 gemini_live_stream_client.py
python3 audio_video_multiplexer.py

echo "Validation successful!"

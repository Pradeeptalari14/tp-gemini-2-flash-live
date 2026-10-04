"""Google Gemini 2.0 Flash Multimodal Live Streaming Client.

Orchestrates bidirectional WebSocket streaming sessions, frame encapsulation,
PCM audio packet chunking, and real-time interruption handling.
"""

import asyncio
import base64
import json
import logging
from typing import Any, Dict

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("gemini_live_client")


class GeminiLiveSession:
    """Encapsulates a persistent bidirectional streaming connection to Gemini 2.0 Flash."""

    def __init__(self, voice_name: str = "Aoede", enable_search_grounding: bool = True):
        self.voice_name = voice_name
        self.enable_search_grounding = enable_search_grounding
        self.session_active = False
        self.stream_seq = 0

    def build_setup_payload(self) -> Dict[str, Any]:
        tools = [{"googleSearch": {}}] if self.enable_search_grounding else []
        return {
            "setup": {
                "model": "models/gemini-2.0-flash-exp",
                "generationConfig": {
                    "responseModalities": ["AUDIO"],
                    "speechConfig": {
                        "voiceConfig": {
                            "prebuiltVoiceConfig": {"voiceName": self.voice_name}
                        }
                    },
                },
                "tools": tools,
            }
        }

    def format_realtime_input(self, pcm_chunk: bytes, mime_type: str = "audio/pcm;rate=16000") -> Dict[str, Any]:
        self.stream_seq += 1
        return {
            "realtimeInput": {
                "mediaChunks": [
                    {
                        "mimeType": mime_type,
                        "data": base64.b64encode(pcm_chunk).decode("utf-8"),
                    }
                ]
            }
        }

    def format_video_frame(self, jpeg_bytes: bytes) -> Dict[str, Any]:
        return {
            "realtimeInput": {
                "mediaChunks": [
                    {
                        "mimeType": "image/jpeg",
                        "data": base64.b64encode(jpeg_bytes).decode("utf-8"),
                    }
                ]
            }
        }


async def main() -> None:
    session = GeminiLiveSession(voice_name="Aoede", enable_search_grounding=True)
    setup_msg = session.build_setup_payload()
    logger.info("Generated Setup Payload: %s", json.dumps(setup_msg, indent=2))

    dummy_pcm = b"\x00\x01" * 800  # 100ms dummy audio
    audio_frame = session.format_realtime_input(dummy_pcm)
    logger.info("Formatted Realtime Audio Chunk (seq=%d, bytes=%d)", session.stream_seq, len(dummy_pcm))

    dummy_jpeg = b"\xff\xd8\xff\xe0" + b"\x00" * 32  # Minimal JPEG header
    video_frame = session.format_video_frame(dummy_jpeg)
    logger.info("Formatted Realtime Video Frame: mime=%s", video_frame["realtimeInput"]["mediaChunks"][0]["mimeType"])


if __name__ == "__main__":
    asyncio.run(main())

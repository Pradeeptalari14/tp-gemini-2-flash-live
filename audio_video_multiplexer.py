"""Audio and Video Multiplexer for Gemini 2.0 Flash Live.

Synchronizes audio PCM frames and camera video captures into interleaved
chronological payloads, preventing drift across high-bandwidth modalities.
"""

import logging
import time
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("av_multiplexer")


class AVStreamMultiplexer:
    """Interleaves audio and video packets into a monotonic sequence."""

    def __init__(self, target_fps: int = 2):
        self.target_fps = target_fps
        self.frame_interval_sec = 1.0 / target_fps
        self.last_video_ts: float = 0.0
        self.queue: List[Dict[str, Any]] = []

    def ingest_audio(self, pcm_bytes: bytes) -> Dict[str, Any]:
        ts = time.time()
        packet = {"type": "audio", "timestamp": ts, "size_bytes": len(pcm_bytes)}
        self.queue.append(packet)
        return packet

    def ingest_video_candidate(self, jpeg_bytes: bytes) -> Dict[str, Any]:
        now = time.time()
        if (now - self.last_video_ts) >= self.frame_interval_sec:
            self.last_video_ts = now
            packet = {"type": "video", "timestamp": now, "size_bytes": len(jpeg_bytes), "status": "forwarded"}
            self.queue.append(packet)
            logger.info("Forwarded video frame at ts=%.3f (size=%d)", now, len(jpeg_bytes))
            return packet
        return {"type": "video", "timestamp": now, "status": "dropped_rate_limit"}


def run_multiplexer_demo() -> None:
    mux = AVStreamMultiplexer(target_fps=2)
    # Simulate 5 fast video frames and audio
    mux.ingest_audio(b"audio_bytes_1")
    p1 = mux.ingest_video_candidate(b"jpeg_frame_1")
    p2 = mux.ingest_video_candidate(b"jpeg_frame_2")

    logger.info("Frame 1 status: %s", p1.get("status"))
    logger.info("Frame 2 status: %s", p2.get("status"))


if __name__ == "__main__":
    run_multiplexer_demo()

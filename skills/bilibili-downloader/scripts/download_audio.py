#!/usr/bin/env python3
"""
Bilibili Audio Downloader Script
Usage: python download_audio.py <bvid_or_url>

Default output directory: ~/Downloaders/OpenClaw/bilibili/
"""

import os
import sys
from pathlib import Path
from bilibili_api import video, sync

# 默认下载目录
DEFAULT_OUTPUT_DIR = Path.home() / "Downloaders" / "OpenClaw" / "bilibili"


def download_audio(bvid, output_path=None):
    """Download audio from a Bilibili video."""
    if output_path is None:
        output_path = DEFAULT_OUTPUT_DIR
    
    # 确保目录存在
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    v = video.Video(bvid=bvid)
    info = v.get_info()
    filename = f"{info['title'][:50]}.mp3".replace("/", "_").replace(":", "_")
    output_file = str(Path(output_path) / filename)

    sync(v.download_audio(output=output_file))

    print(f"✅ 音频已下载：{output_file}")
    return output_file


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    bvid = sys.argv[1]
    download_audio(bvid)

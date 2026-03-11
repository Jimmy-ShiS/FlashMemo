#!/usr/bin/env python3
"""
Bilibili Subtitle Downloader Script
Usage: python download_subtitles.py <bvid_or_url>

Default output directory: ~/Downloaders/OpenClaw/bilibili/
"""

import os
import sys
from pathlib import Path
from bilibili_api import video, sync

# 默认下载目录
DEFAULT_OUTPUT_DIR = Path.home() / "Downloaders" / "OpenClaw" / "bilibili"


def download_subtitles(bvid, output_path=None):
    """Download subtitles from a Bilibili video."""
    if output_path is None:
        output_path = DEFAULT_OUTPUT_DIR
    
    # 确保目录存在
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    v = video.Video(bvid=bvid)
    
    sync(v.download_subtitle(output=str(Path(output_path))))

    print(f"✅ 字幕已下载到：{output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    bvid = sys.argv[1]
    download_subtitles(bvid)

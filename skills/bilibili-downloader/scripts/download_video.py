#!/usr/bin/env python3
"""
Bilibili Video Downloader Script
Usage: python download_video.py <bvid_or_url> [quality]
Quality: 127=8K, 126=杜比，125=1080P+, 120=1080P, 116=4K, 112=1080P, 80=1080P, 74=720P, 64=480P, 32=360P

Default output directory: ~/Downloaders/OpenClaw/bilibili/
"""

import os
import sys
from pathlib import Path
from bilibili_api import video, sync

# 默认下载目录
DEFAULT_OUTPUT_DIR = Path.home() / "Downloaders" / "OpenClaw" / "bilibili"


def download_video(bvid, output_path=None, quality=None):
    """Download a single Bilibili video."""
    if output_path is None:
        output_path = DEFAULT_OUTPUT_DIR
    
    # 确保目录存在
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    v = video.Video(bvid=bvid)
    info = v.get_info()
    filename = f"{info['title'][:50]}.mp4".replace("/", "_").replace(":", "_")
    output_file = str(Path(output_path) / filename)

    if quality:
        url_info = v.get_download_url(qn=int(quality))
        sync(v.download(output=output_file, url=url_info))
    else:
        sync(v.download(output=output_file))

    print(f"✅ 已下载：{output_file}")
    return output_file


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    bvid = sys.argv[1]
    quality = sys.argv[2] if len(sys.argv) > 2 else None

    download_video(bvid, None, quality)

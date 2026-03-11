#!/usr/bin/env python3
"""
Faster Whisper 语音转录脚本
默认使用 base 模型，平衡速度和准确度
"""

import argparse
import sys
from pathlib import Path

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("❌ 错误：faster-whisper 未安装", file=sys.stderr)
    print("请运行：pip3 install --break-system-packages faster-whisper", file=sys.stderr)
    sys.exit(1)


def transcribe(audio_path: str, model_size: str = "base", device: str = "auto"):
    """
    转录音频文件为文字
    
    Args:
        audio_path: 音频文件路径
        model_size: 模型大小 (tiny, base, small, medium, large-v2, large-v3)
        device: 设备 (auto, cpu, cuda)
    """
    print(f"🎤 开始转录：{audio_path}")
    print(f"📦 使用模型：{model_size}")
    
    # 加载模型
    model = WhisperModel(model_size, device=device, compute_type="int8")
    
    # 转录
    segments, info = model.transcribe(audio_path, beam_size=5)
    
    print(f"ℹ️  检测语言：{info.language} (概率：{info.language_probability:.2f})")
    print(f"⏱️  音频时长：{info.duration:.2f}秒")
    print()
    
    # 收集所有转录文本
    full_text = []
    for segment in segments:
        text = f"[{segment.start:.2f}s → {segment.end:.2f}s] {segment.text}"
        print(text)
        full_text.append(segment.text.strip())
    
    print()
    print("=" * 50)
    print("📝 完整转录：")
    print(" ".join(full_text))
    print("=" * 50)
    
    return " ".join(full_text)


def main():
    parser = argparse.ArgumentParser(
        description="Faster Whisper 语音转录工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s audio.ogg                    # 使用默认 base 模型
  %(prog)s audio.wav -m tiny           # 使用 tiny 模型 (最快)
  %(prog)s audio.mp3 -m small -d cuda  # 使用 small 模型 + GPU
        """
    )
    
    parser.add_argument("audio_file", help="音频文件路径 (.ogg, .wav, .mp3, .flac 等)")
    parser.add_argument("-m", "--model", default="base",
                        choices=["tiny", "base", "small", "medium", "large-v2", "large-v3"],
                        help="模型大小 (默认：base)")
    parser.add_argument("-d", "--device", default="auto",
                        choices=["auto", "cpu", "cuda"],
                        help="运行设备 (默认：auto)")
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not Path(args.audio_file).exists():
        print(f"❌ 错误：文件不存在：{args.audio_file}", file=sys.stderr)
        sys.exit(1)
    
    # 执行转录
    try:
        result = transcribe(args.audio_file, args.model, args.device)
        print()
        print("✅ 转录完成")
    except Exception as e:
        print(f"❌ 转录失败：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

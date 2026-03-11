# Voice Transcription Skill

使用 Faster Whisper 进行本地语音转录（隐私优先）。

## 要求

```bash
pip3 install --break-system-packages faster-whisper
```

## 使用方法

```bash
# 转录语音文件（默认使用 medium 模型，高准确度）
python3 ~/.openclaw/workspace/skills/faster-whisper-transcribe/voice_transcribe.py /path/to/audio.ogg

# 或使用便捷命令
~/.openclaw/workspace/skills/faster-whisper-transcribe/voice_transcribe.py ~/.openclaw/media/inbound/file_xxx.ogg
```

## 模型选项

| 模型 | 速度 | 准确度 | 内存占用 | 适用场景 |
|------|------|--------|----------|----------|
| `tiny` | ⚡⚡⚡ 最快 | ⭐ 较低 | ~143 MB | 快速测试 |
| `base` | ⚡⚡ 平衡 | ⭐⭐ 中等 | ~143 MB | 日常使用 |
| `small` | ⚡ 较慢 | ⭐⭐⭐ 较好 | ~488 MB | 高精度需求 |
| `medium` | 🐌 慢 | ⭐⭐⭐⭐ 高 | ~1.5 GB | **专业转录（默认）** |
| `large-v2/v3` | 🐌🐌 最慢 | ⭐⭐⭐⭐⭐ 最高 | ~3 GB | 专业场景 |

## 命令行参数

```bash
# 使用默认 base 模型
voice_transcribe.py audio.ogg

# 指定模型
voice_transcribe.py audio.ogg -m tiny      # 最快
voice_transcribe.py audio.ogg -m small     # 更准确

# 使用 GPU（如果有）
voice_transcribe.py audio.ogg -d cuda
```

## 输出格式

- 分段显示时间戳和文本
- 最后输出完整转录文本
- 自动检测语言

## 示例输出

```
🎤 开始转录：audio.ogg
📦 使用模型：base
ℹ️  检测语言：zh (概率：0.98)
⏱️  音频时长：5.32 秒

[0.00s → 2.50s] 你好，这是一个测试
[2.50s → 5.32s] 语音转录功能正常工作

==================================================
📝 完整转录：
你好，这是一个测试 语音转录功能正常工作
==================================================
✅ 转录完成
```

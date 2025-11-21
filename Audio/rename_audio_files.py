# -*- coding: utf-8 -*-
"""
NDC 语音文件重命名脚本
按时间顺序将生成的文件重命名为标准格式
"""

import json
import os
import sys

# ===== 配置 =====
CONFIG_FILE = r"D:\NDC_project\第一章内容（对话修正版）\scene1_tommy_dialogues.json"
OUTPUT_DIR = r"D:\NDC_project\Audio\Voice\Episode1\Loop1\Tommy"

def load_config():
    """加载配置文件"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_expected_filename(dialogue, index):
    """生成期望的文件名"""
    character = dialogue['character']
    sequence = f"{index+1:06d}"
    return f"{character}_{sequence}.mp3"

def rename_files():
    """重命名文件"""
    print("=" * 60)
    print("NDC Audio Rename Tool")
    print("=" * 60)

    # 加载配置
    print("\n[1] Loading config...")
    config = load_config()
    print(f"    Config loaded: {len(config)} dialogues")

    # 获取所有mp3文件
    print("\n[2] Scanning audio files...")
    files = []
    for filename in os.listdir(OUTPUT_DIR):
        if filename.endswith('.mp3'):
            filepath = os.path.join(OUTPUT_DIR, filename)
            mtime = os.path.getmtime(filepath)
            files.append((filename, filepath, mtime))

    # 按时间排序
    files.sort(key=lambda x: x[2])
    print(f"    Found {len(files)} audio files")

    # 重命名
    print("\n[3] Renaming files...")
    renamed_count = 0

    for i, (old_name, old_path, _) in enumerate(files):
        if i < len(config):
            new_name = get_expected_filename(config[i], i)
            new_path = os.path.join(OUTPUT_DIR, new_name)

            # 如果已经是正确名称,跳过
            if old_name == new_name:
                print(f"    [{i+1:2d}] SKIP: {new_name} (already correct)")
                continue

            # 重命名
            try:
                os.rename(old_path, new_path)
                print(f"    [{i+1:2d}] OK: {old_name}")
                print(f"         -> {new_name}")
                renamed_count += 1
            except Exception as e:
                print(f"    [{i+1:2d}] ERROR: {e}")
        else:
            print(f"    [{i+1:2d}] SKIP: {old_name} (no config)")

    print(f"\n[4] Done! Renamed {renamed_count}/{len(files)} files")
    print("=" * 60)

if __name__ == "__main__":
    try:
        rename_files()
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

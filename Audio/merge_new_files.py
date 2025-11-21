"""
使用新生成的正确文件合并Loop1 Opening音频
从Voice/Episode1/Loop1/目录读取
"""

import json
import os

def load_config():
    config_path = r"D:\NDC_project\Audio\Config\Loop1_Opening_AVG_config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    dialogues = load_config()

    print("Loop1 Opening - Merge New Generated Files")
    print("=" * 60)

    # Output file
    output_path = r"D:\NDC_project\Audio\Loop1_Opening_Complete_New.mp3"

    found_count = 0
    missing_count = 0

    with open(output_path, 'wb') as outfile:
        for i, dialogue in enumerate(dialogues, 1):
            # 构建完整路径
            scene_path = dialogue['output_path']  # Audio/Voice/Episode1/Loop1/Opening/
            full_path = os.path.join(r"D:\NDC_project", scene_path)
            filename = dialogue['output_filename']  # Zack_001001.mp3
            audio_file = os.path.join(full_path, filename)

            character = dialogue['character_name']
            scene = dialogue['scene']

            print(f"[{i:2d}/{len(dialogues)}] [{scene:7s}] {filename:20s}", end=" ")

            if not os.path.exists(audio_file):
                print("[MISSING]")
                missing_count += 1
                continue

            try:
                # 读取并写入二进制数据
                with open(audio_file, 'rb') as infile:
                    data = infile.read()
                    outfile.write(data)

                file_size = len(data) / 1024  # KB
                print(f"[OK] {file_size:.1f}KB")
                found_count += 1
            except Exception as e:
                print(f"[ERROR] {e}")
                missing_count += 1

    print("=" * 60)
    print(f"Success: {found_count}/{len(dialogues)} files merged")
    print(f"Missing: {missing_count} files")
    print(f"\nOutput: {output_path}")

    # 检查输出文件大小
    if os.path.exists(output_path):
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"Size: {size_mb:.2f} MB")

if __name__ == "__main__":
    main()

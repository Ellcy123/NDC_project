"""
合并Loop1 Opening所有音频为完整文件
"""

import json
import os
from pydub import AudioSegment

def load_config():
    config_path = r"D:\NDC_project\Audio\Config\Loop1_Opening_AVG_config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    dialogues = load_config()

    print("Loop1 Opening Audio Merge Tool")
    print("=" * 60)

    # 合并所有音频
    combined = AudioSegment.empty()
    pause_duration = 800  # 800ms pause between dialogues

    missing_files = []

    for i, dialogue in enumerate(dialogues, 1):
        scene_path = dialogue['output_path']
        full_path = os.path.join(r"D:\NDC_project", scene_path)
        audio_file = os.path.join(full_path, dialogue['output_filename'])

        print(f"[{i}/{len(dialogues)}] {dialogue['output_filename']}", end=" ")

        if not os.path.exists(audio_file):
            print("[MISSING]")
            missing_files.append(dialogue['output_filename'])
            continue

        try:
            # Load audio segment
            segment = AudioSegment.from_mp3(audio_file)
            combined += segment

            # Add pause (except after last segment)
            if i < len(dialogues):
                combined += AudioSegment.silent(duration=pause_duration)

            print("[OK]")
        except Exception as e:
            print(f"[ERROR] {e}")
            missing_files.append(dialogue['output_filename'])

    # Export final merged audio
    output_path = r"D:\NDC_project\Audio\Loop1_Opening_Complete.mp3"
    print(f"\nExporting to: {output_path}")
    combined.export(output_path, format="mp3", bitrate="128k")

    print("=" * 60)
    print(f"[SUCCESS] Merged audio saved!")
    print(f"Duration: {len(combined) / 1000:.2f} seconds ({len(combined) / 60000:.2f} minutes)")
    print(f"Segments: {len(dialogues) - len(missing_files)}/{len(dialogues)}")

    if missing_files:
        print(f"\nMissing files: {len(missing_files)}")
        for f in missing_files:
            print(f"  - {f}")

if __name__ == "__main__":
    main()

"""
Merge all generated dialogue audio files into one complete file.
Run after generating all dialogue segments.
"""

import json
import os
import glob
from pydub import AudioSegment

def load_config():
    config_path = r"D:\NDC_project\Audio\Config\Loop1_Opening_AVG_config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    dialogues = load_config()
    temp_dir = r"D:\NDC_project\Audio\temp_opening"
    output_path = r"D:\NDC_project\Audio\Loop1_Opening_Full.mp3"

    print(f"Loading dialogues from: {temp_dir}")
    print(f"Total expected segments: {len(dialogues)}")
    print("=" * 60)

    # Find all generated audio files in temp directory
    audio_files = sorted(glob.glob(os.path.join(temp_dir, "*.mp3")))

    if not audio_files:
        print(f"ERROR: No audio files found in {temp_dir}")
        return

    print(f"Found {len(audio_files)} audio files:")
    for f in audio_files:
        print(f"  {os.path.basename(f)}")

    if len(audio_files) < len(dialogues):
        print(f"\nWARNING: Only found {len(audio_files)}/{len(dialogues)} files")
        print("Some dialogues may be missing!")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return

    print("\n" + "=" * 60)
    print("Merging audio files...")

    # Merge all audio files with pauses
    combined = AudioSegment.empty()
    pause_duration = 800  # 800ms pause between dialogues

    for i, audio_file in enumerate(audio_files, 1):
        print(f"[{i}/{len(audio_files)}] Adding: {os.path.basename(audio_file)}")

        try:
            # Load audio segment
            segment = AudioSegment.from_mp3(audio_file)

            # Add to combined audio
            combined += segment

            # Add pause between segments (except after last segment)
            if i < len(audio_files):
                combined += AudioSegment.silent(duration=pause_duration)

        except Exception as e:
            print(f"  ERROR loading {audio_file}: {e}")
            continue

    # Export final merged audio
    print(f"\nExporting final audio to: {output_path}")
    combined.export(output_path, format="mp3", bitrate="128k")

    print("=" * 60)
    print(f"[SUCCESS] Final audio saved to:")
    print(f"  {output_path}")
    print(f"\nTotal duration: {len(combined) / 1000:.2f} seconds ({len(combined) / 60000:.2f} minutes)")
    print(f"Total segments: {len(audio_files)}")
    print("\n[DONE] Merge complete!")

if __name__ == "__main__":
    main()

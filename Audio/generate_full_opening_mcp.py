import json
import os
import time
from pydub import AudioSegment

# Load config
config_path = r"D:\NDC_project\Audio\Config\Loop1_Opening_AVG_config.json"
with open(config_path, 'r', encoding='utf-8') as f:
    dialogues = json.load(f)

# Create temp directory for individual audio files
temp_dir = r"D:\NDC_project\Audio\temp_opening"
os.makedirs(temp_dir, exist_ok=True)

print(f"Starting generation of {len(dialogues)} dialogue segments...")
print("=" * 60)
print("\nNOTE: This script requires manual execution of ElevenLabs API calls.")
print("Please use the MCP tool mcp__elevenlabs__text_to_speech for each segment.")
print("\nGenerated command list for each dialogue:")
print("=" * 60)

# Generate list of files that should exist
expected_files = []
for i, dialogue in enumerate(dialogues, 1):
    filename = f"{i:03d}_{dialogue['id']}.mp3"
    expected_files.append(os.path.join(temp_dir, filename))

    print(f"\n[{i}/{len(dialogues)}] {dialogue['character_name']}")
    print(f"  Text: {dialogue['text_en']}")
    print(f"  Save as: {filename}")

print("\n" + "=" * 60)
print("After generating all audio files manually, run merge step:")
print(f"python -c \"from pydub import AudioSegment; import os; ")
print(f"files = {expected_files}; ")
print(f"combined = AudioSegment.empty(); ")
print(f"[combined := combined + AudioSegment.from_mp3(f) + AudioSegment.silent(800) for f in files]; ")
print(f"combined.export(r'D:\\NDC_project\\Audio\\Loop1_Opening_Full.mp3', format='mp3')\"")

import json
import os
import time
from elevenlabs.client import ElevenLabs
from elevenlabs import save
from pydub import AudioSegment

# Initialize ElevenLabs client (will use ELEVENLABS_API_KEY env variable)
# Make sure ELEVENLABS_API_KEY is set in your environment
api_key = os.getenv('ELEVENLABS_API_KEY')
if not api_key:
    raise ValueError("ELEVENLABS_API_KEY environment variable not set")
client = ElevenLabs(api_key=api_key)

# Load config
config_path = r"D:\NDC_project\Audio\Config\Loop1_Opening_AVG_config.json"
with open(config_path, 'r', encoding='utf-8') as f:
    dialogues = json.load(f)

# Create temp directory for individual audio files
temp_dir = r"D:\NDC_project\Audio\temp_opening"
os.makedirs(temp_dir, exist_ok=True)

print(f"Starting generation of {len(dialogues)} dialogue segments...")
print("=" * 60)

# Generate all audio files
audio_files = []
for i, dialogue in enumerate(dialogues, 1):
    text = dialogue['text_en']
    voice_config = dialogue['voice_config']
    character = dialogue['character_name']
    output_file = os.path.join(temp_dir, f"{i:03d}_{dialogue['id']}.mp3")

    print(f"[{i}/{len(dialogues)}] Generating: {character}")
    print(f"  Text: {text[:50]}{'...' if len(text) > 50 else ''}")

    try:
        # Generate audio
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=voice_config.get('voice_id'),
            model_id=voice_config['model_id'],
            voice_settings={
                "stability": voice_config['stability'],
                "similarity_boost": voice_config['similarity_boost'],
                "style": voice_config.get('style', 0),
                "use_speaker_boost": voice_config.get('use_speaker_boost', True)
            },
            output_format=voice_config['output_format']
        )

        # Save audio
        save(audio, output_file)
        audio_files.append(output_file)
        print(f"  [OK] Saved: {output_file}")

        # Small delay to avoid rate limiting
        time.sleep(0.5)

    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        continue

    print()

print("=" * 60)
print(f"Generated {len(audio_files)} audio files")
print("\nMerging audio files...")

# Merge all audio files with pauses
combined = AudioSegment.empty()
pause_duration = 800  # 800ms pause between dialogues

for i, audio_file in enumerate(audio_files, 1):
    print(f"Adding segment {i}/{len(audio_files)}: {os.path.basename(audio_file)}")

    # Load audio segment
    segment = AudioSegment.from_mp3(audio_file)

    # Add to combined audio
    combined += segment

    # Add pause between segments (except after last segment)
    if i < len(audio_files):
        combined += AudioSegment.silent(duration=pause_duration)

# Export final merged audio
output_path = r"D:\NDC_project\Audio\Loop1_Opening_Full.mp3"
print(f"\nExporting final audio to: {output_path}")
combined.export(output_path, format="mp3", bitrate="128k")

print("=" * 60)
print(f"[SUCCESS] Final audio saved to:")
print(f"  {output_path}")
print(f"\nTotal duration: {len(combined) / 1000:.2f} seconds ({len(combined) / 60000:.2f} minutes)")
print(f"Total segments: {len(audio_files)}")

# Clean up temp files
print("\nCleaning up temporary files...")
for audio_file in audio_files:
    try:
        os.remove(audio_file)
        print(f"  Deleted: {os.path.basename(audio_file)}")
    except:
        pass

try:
    os.rmdir(temp_dir)
    print(f"  Removed temp directory: {temp_dir}")
except:
    print(f"  Could not remove temp directory (may not be empty)")

print("\n[DONE] All complete!")

"""
生成道具分析旁白语音 - Zack 内心独白 1301-1304（英文版）
语气：思考推理，平静略带疲惫
"""

import os
import requests

API_KEY = "sk_4d9d6805ebd1e8bc7dfea19fee48793df236f72e34e1ce3b"
VOICE_ID = "WgbPnNyYdbv9FY7QRE9Y"  # Zack
MODEL_ID = "eleven_multilingual_v2"
OUTPUT_DIR = r"D:\NDC_project\AVG\audio\item_analysis"

dialogues = [
    {
        "id": "1301",
        "text": "It's too dark inside the barrel to see if there's any gunpowder residue. I need to find some light and take a closer look.",
        "stability": 0.75,
        "similarity_boost": 0.80,
        "style": 0.35,
        "speed": 0.90,
    },
    {
        "id": "1302",
        "text": "The stain on the photo doesn't look like a regular water mark. It smells like lemon juice... maybe heating it up will reveal something.",
        "stability": 0.75,
        "similarity_boost": 0.80,
        "style": 0.35,
        "speed": 0.90,
    },
    {
        "id": "1303",
        "text": "This combination lock belongs to Rosa. Are there any number-related clues? I need to look around.",
        "stability": 0.75,
        "similarity_boost": 0.80,
        "style": 0.35,
        "speed": 0.90,
    },
    {
        "id": "1304",
        "text": "The stamp on the shell casing is too faded to read. I need to figure out a way to make it legible.",
        "stability": 0.75,
        "similarity_boost": 0.80,
        "style": 0.35,
        "speed": 0.90,
    },
]

headers = {
    "xi-api-key": API_KEY,
    "Content-Type": "application/json",
    "Accept": "audio/mpeg",
}

os.makedirs(OUTPUT_DIR, exist_ok=True)

for d in dialogues:
    out_path = os.path.join(OUTPUT_DIR, f"{d['id']}.mp3")
    payload = {
        "text": d["text"],
        "model_id": MODEL_ID,
        "voice_settings": {
            "stability": d["stability"],
            "similarity_boost": d["similarity_boost"],
            "style": d["style"],
            "use_speaker_boost": True,
            "speed": d["speed"],
        },
        "language_code": "en",
    }
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}?output_format=mp3_44100_128"
    print(f"Generating {d['id']}.mp3 ...")
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code == 200:
        with open(out_path, "wb") as f:
            f.write(resp.content)
        print(f"  OK -> {out_path}")
    else:
        print(f"  ERROR {resp.status_code}: {resp.text[:200]}")

print("Done.")

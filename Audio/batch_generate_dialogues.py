"""
Batch generation script for Loop1 Opening dialogues.
This script will generate audio files in batches to avoid API limits.
Run with: python batch_generate_dialogues.py --batch <batch_number>
"""

import json
import os
import sys
import argparse

def load_config():
    config_path = r"D:\NDC_project\Audio\Config\Loop1_Opening_AVG_config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def print_mcp_command(dialogue, index, temp_dir):
    """Print the MCP command needed to generate this dialogue"""
    vc = dialogue['voice_config']
    filename = f"{index:03d}_{dialogue['id']}.mp3"
    filepath = os.path.join(temp_dir, filename)

    print(f"\n--- Dialogue {index}: {dialogue['character_name']} ---")
    print(f"Text: {dialogue['text_en']}")
    print(f"Output: {filename}")
    print(f"\nMCP Command:")
    print(f'mcp__elevenlabs__text_to_speech(')
    print(f'  text="{dialogue["text_en"]}",')
    print(f'  voice_name="{vc.get("voice_name", "Adam")}",')
    print(f'  model_id="{vc["model_id"]}",')
    print(f'  stability={vc["stability"]},')
    print(f'  similarity_boost={vc["similarity_boost"]},')
    print(f'  style={vc.get("style", 0)},')
    print(f'  speed={vc.get("speed", 1.0)},')
    print(f'  language="{vc["language"]}",')
    print(f'  output_directory="{temp_dir}"')
    print(f')')

    return filepath

def main():
    parser = argparse.ArgumentParser(description='Generate dialogue audio files in batches')
    parser.add_argument('--batch', type=int, help='Batch number (1-5)', default=0)
    parser.add_argument('--batch-size', type=int, default=10, help='Number of dialogues per batch')
    parser.add_argument('--list-all', action='store_true', help='List all dialogues')

    args = parser.parse_args()

    dialogues = load_config()
    temp_dir = r"D:\NDC_project\Audio\temp_opening"
    os.makedirs(temp_dir, exist_ok=True)

    print(f"Total dialogues: {len(dialogues)}")
    print(f"Batch size: {args.batch_size}")
    print(f"Total batches: {(len(dialogues) + args.batch_size - 1) // args.batch_size}")

    if args.list_all:
        print("\n" + "="*60)
        print("ALL DIALOGUES:")
        print("="*60)
        for i, d in enumerate(dialogues, 1):
            print(f"{i}. [{d['character_name']}] {d['text_en'][:50]}...")
        return

    if args.batch == 0:
        print("\nUsage:")
        print("  python batch_generate_dialogues.py --batch 1    # Generate batch 1")
        print("  python batch_generate_dialogues.py --list-all   # List all dialogues")
        return

    # Calculate batch range
    start_idx = (args.batch - 1) * args.batch_size
    end_idx = min(start_idx + args.batch_size, len(dialogues))

    if start_idx >= len(dialogues):
        print(f"Error: Batch {args.batch} is out of range")
        return

    print(f"\n{'='*60}")
    print(f"BATCH {args.batch}: Dialogues {start_idx + 1} to {end_idx}")
    print(f"{'='*60}")

    expected_files = []
    for i in range(start_idx, end_idx):
        dialogue = dialogues[i]
        filepath = print_mcp_command(dialogue, i + 1, temp_dir)
        expected_files.append(filepath)

    print(f"\n{'='*60}")
    print(f"Expected files for this batch:")
    for f in expected_files:
        print(f"  {os.path.basename(f)}")

if __name__ == "__main__":
    main()

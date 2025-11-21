"""
重命名Loop1 Opening音频文件为标准格式
"""

import json
import os
import glob

def load_config():
    config_path = r"D:\NDC_project\Audio\Config\Loop1_Opening_AVG_config.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_file_creation_time(filepath):
    return os.path.getctime(filepath)

def main():
    dialogues = load_config()

    # 按场景分组
    scenes = {}
    for d in dialogues:
        scene = d['scene']
        if scene not in scenes:
            scenes[scene] = []
        scenes[scene].append(d)

    print("Loop1 Opening Audio Rename Tool")
    print("=" * 60)

    total_renamed = 0

    for scene_name, scene_dialogues in scenes.items():
        scene_path = scene_dialogues[0]['output_path']
        full_path = os.path.join(r"D:\NDC_project", scene_path)

        print(f"\nScene: {scene_name}")
        print(f"Path: {full_path}")

        # 获取所有mp3文件,按创建时间排序
        mp3_files = glob.glob(os.path.join(full_path, "*.mp3"))
        mp3_files.sort(key=get_file_creation_time)

        print(f"Found {len(mp3_files)} files, expect {len(scene_dialogues)} files")

        # 按顺序重命名
        for i, dialogue in enumerate(scene_dialogues):
            if i >= len(mp3_files):
                print(f"  [MISSING] {dialogue['output_filename']}")
                continue

            old_file = mp3_files[i]
            old_name = os.path.basename(old_file)
            new_name = dialogue['output_filename']
            new_file = os.path.join(full_path, new_name)

            # 跳过已正确命名的
            if old_name == new_name:
                print(f"  [OK] {new_name}")
                continue

            # 删除已存在的目标文件
            if os.path.exists(new_file) and old_file != new_file:
                os.remove(new_file)

            # 重命名
            try:
                os.rename(old_file, new_file)
                print(f"  [RENAMED] {old_name} -> {new_name}")
                total_renamed += 1
            except Exception as e:
                print(f"  [ERROR] Failed to rename {old_name}: {e}")

    print("\n" + "=" * 60)
    print(f"Renamed {total_renamed} files")

if __name__ == "__main__":
    main()

import json
import os
from datetime import datetime

# 读取配置文件
config_path = r"D:\NDC_project\Audio\Config\Loop1_Opening_AVG_config.json"
temp_dir = r"D:\NDC_project\Audio\temp_opening"

print("正在读取配置文件...")
with open(config_path, 'r', encoding='utf-8') as f:
    dialogues = json.load(f)

print(f"配置文件包含 {len(dialogues)} 段对话")

# 按ID排序对话
dialogues_sorted = sorted(dialogues, key=lambda x: x['id'])

# 获取所有生成的音频文件
generated_files = {}
for filename in os.listdir(temp_dir):
    if filename.endswith('.mp3'):
        filepath = os.path.join(temp_dir, filename)
        # 从文件名提取时间戳
        timestamp = filename.split('_')[-1].replace('.mp3', '')
        generated_files[timestamp] = {
            'filename': filename,
            'filepath': filepath
        }

print(f"找到 {len(generated_files)} 个音频文件")

# 按时间戳排序文件
sorted_timestamps = sorted(generated_files.keys())

# 创建ffmpeg concat文件列表
concat_file_path = r"D:\NDC_project\Audio\concat_list.txt"
with open(concat_file_path, 'w', encoding='utf-8') as f:
    for i, ts in enumerate(sorted_timestamps, 1):
        filename = generated_files[ts]['filename']
        # ffmpeg concat需要相对路径或绝对路径
        f.write(f"file 'temp_opening/{filename}'\n")
        # 在每个文件后添加800ms静音(除了最后一个)
        if i < len(sorted_timestamps):
            # 创建一个临时静音指令(需要单独生成静音文件)
            pass

print(f"\n已创建ffmpeg concat列表文件: {concat_file_path}")

# 创建详细的文件顺序报告
report_path = r"D:\NDC_project\Audio\file_order_report.txt"
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("Loop1 Opening 音频文件顺序报告\n")
    f.write("="*80 + "\n")
    f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write(f"配置文件: {config_path}\n")
    f.write(f"对话总数: {len(dialogues)}\n")
    f.write(f"生成文件数: {len(sorted_timestamps)}\n\n")

    f.write("文件顺序(按时间戳排序):\n")
    f.write("-"*80 + "\n")
    for i, ts in enumerate(sorted_timestamps, 1):
        filename = generated_files[ts]['filename']
        f.write(f"{i:3d}. {filename}\n")

    f.write("\n" + "="*80 + "\n")
    f.write("使用ffmpeg合并文件的命令:\n\n")
    f.write(f"cd D:\\NDC_project\\Audio\n")
    f.write(f"ffmpeg -f concat -safe 0 -i concat_list.txt -c copy Loop1_Opening_Full.mp3\n\n")
    f.write("注意: 此命令不会添加对话之间的停顿。\n")
    f.write("如需添加800ms停顿,需要使用更复杂的ffmpeg filter或使用pydub。\n\n")

    f.write("="*80 + "\n")
    f.write("原始对话配置顺序:\n")
    f.write("-"*80 + "\n")
    for i, dlg in enumerate(dialogues_sorted, 1):
        f.write(f"{i:3d}. ID:{dlg['id']} - {dlg['character_name']}: {dlg['text_en'][:50]}...\n")

print(f"已创建详细报告: {report_path}")

# 创建Python简单合并脚本(不使用pydub)
simple_merge_script = r"D:\NDC_project\Audio\simple_merge.py"
with open(simple_merge_script, 'w', encoding='utf-8') as f:
    f.write("""import os

# 简单的二进制文件连接(仅适用于相同格式的MP3文件)
temp_dir = r"D:\\NDC_project\\Audio\\temp_opening"
output_file = r"D:\\NDC_project\\Audio\\Loop1_Opening_Full.mp3"

# 获取所有MP3文件并按时间戳排序
files = []
for filename in os.listdir(temp_dir):
    if filename.endswith('.mp3'):
        timestamp = filename.split('_')[-1].replace('.mp3', '')
        files.append((timestamp, os.path.join(temp_dir, filename)))

files.sort(key=lambda x: x[0])

print(f"找到 {len(files)} 个音频文件")
print("开始合并...")

# 简单的二进制连接(注意:这种方法可能不完美,因为MP3有头部信息)
with open(output_file, 'wb') as outfile:
    for i, (ts, filepath) in enumerate(files, 1):
        print(f"[{i}/{len(files)}] 添加: {os.path.basename(filepath)}")
        with open(filepath, 'rb') as infile:
            outfile.write(infile.read())

print(f"\\n合并完成!文件保存到: {output_file}")
print("\\n警告: 由于使用了简单的二进制连接,合成的音频可能有问题。")
print("建议安装ffmpeg后使用专业工具合并。")
print("\\n安装ffmpeg: https://ffmpeg.org/download.html")
""")

print(f"已创建简单合并脚本: {simple_merge_script}")
print("\n" + "="*80)
print("由于系统未安装ffmpeg,提供了以下选项:")
print("1. 安装ffmpeg后使用concat_list.txt合并文件")
print("2. 运行simple_merge.py进行简单合并(可能质量不佳)")
print("3. 使用专业音频编辑软件(如Audacity)手动导入并合并")
print("="*80)

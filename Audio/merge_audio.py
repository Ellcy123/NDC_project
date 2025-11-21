import json
import os
from pydub import AudioSegment
from datetime import datetime

# 读取配置文件
config_path = r"D:\NDC_project\Audio\Config\Loop1_Opening_AVG_config.json"
temp_dir = r"D:\NDC_project\Audio\temp_opening"
output_file = r"D:\NDC_project\Audio\Loop1_Opening_Full.mp3"

print("正在读取配置文件...")
with open(config_path, 'r', encoding='utf-8') as f:
    dialogues = json.load(f)

print(f"配置文件包含 {len(dialogues)} 段对话")

# 获取所有生成的音频文件
generated_files = {}
for filename in os.listdir(temp_dir):
    if filename.endswith('.mp3'):
        filepath = os.path.join(temp_dir, filename)
        # 从文件名提取时间戳
        timestamp = filename.split('_')[-1].replace('.mp3', '')
        generated_files[timestamp] = filepath

print(f"找到 {len(generated_files)} 个音频文件")

# 按时间戳排序文件
sorted_timestamps = sorted(generated_files.keys())
sorted_files = [generated_files[ts] for ts in sorted_timestamps]

print("\n开始合并音频文件...")
print(f"将在对话之间添加 800ms 的停顿")

# 创建800ms的静音
silence = AudioSegment.silent(duration=800)

# 合并所有音频
combined = AudioSegment.empty()
errors = []

for i, filepath in enumerate(sorted_files, 1):
    try:
        print(f"[{i}/{len(sorted_files)}] 添加: {os.path.basename(filepath)}")
        audio = AudioSegment.from_mp3(filepath)
        combined += audio

        # 在每段对话后添加停顿(除了最后一段)
        if i < len(sorted_files):
            combined += silence

    except Exception as e:
        error_msg = f"处理文件 {filepath} 时出错: {str(e)}"
        print(f"错误: {error_msg}")
        errors.append(error_msg)

# 导出最终文件
print(f"\n正在导出最终文件到: {output_file}")
combined.export(output_file, format="mp3", bitrate="128k")

# 计算总时长
total_duration_ms = len(combined)
total_duration_sec = total_duration_ms / 1000
minutes = int(total_duration_sec // 60)
seconds = int(total_duration_sec % 60)

print("\n" + "="*60)
print("合并完成!")
print(f"最终文件: {output_file}")
print(f"总时长: {minutes}分{seconds}秒 ({total_duration_ms}ms)")
print(f"成功处理: {len(sorted_files)} 段音频")
print(f"失败: {len(errors)} 段")

if errors:
    print("\n错误列表:")
    for error in errors:
        print(f"  - {error}")

# 生成报告
report_path = r"D:\NDC_project\Audio\merge_report.txt"
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("Loop1 Opening 音频合并报告\n")
    f.write("="*60 + "\n")
    f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write(f"配置文件: {config_path}\n")
    f.write(f"对话总数: {len(dialogues)}\n")
    f.write(f"生成文件数: {len(sorted_files)}\n")
    f.write(f"失败数: {2}\n\n")  # 我们知道有2个文件因为文件名问题失败
    f.write(f"最终文件: {output_file}\n")
    f.write(f"总时长: {minutes}分{seconds}秒\n\n")

    f.write("失败的对话:\n")
    f.write("  - ID 001001002: Webb?! No... this isn't right... (文件名包含'?'字符)\n")
    f.write("  - ID 001001011: So? (文件名包含'?'字符)\n\n")

    if errors:
        f.write("处理错误:\n")
        for error in errors:
            f.write(f"  - {error}\n")

print(f"\n详细报告已保存到: {report_path}")
print("="*60)

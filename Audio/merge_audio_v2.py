import json
import os
from pydub import AudioSegment
from datetime import datetime

# 读取配置文件
config_path = r"D:\NDC_project\Audio\Config\Loop1_Opening_AVG_config.json"
temp_dir = r"D:\NDC_project\Audio\temp_opening"
output_file_wav = r"D:\NDC_project\Audio\Loop1_Opening_Full.wav"
output_file_mp3 = r"D:\NDC_project\Audio\Loop1_Opening_Full.mp3"

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
success_count = 0

for i, filepath in enumerate(sorted_files, 1):
    try:
        print(f"[{i}/{len(sorted_files)}] 添加: {os.path.basename(filepath)}")
        audio = AudioSegment.from_mp3(filepath)
        combined += audio
        success_count += 1

        # 在每段对话后添加停顿(除了最后一段)
        if i < len(sorted_files):
            combined += silence

    except Exception as e:
        error_msg = f"处理文件 {filepath} 时出错: {str(e)}"
        print(f"错误: {error_msg}")
        errors.append(error_msg)

if success_count > 0:
    # 首先导出为WAV (不需要ffmpeg)
    print(f"\n正在导出WAV文件到: {output_file_wav}")
    try:
        combined.export(output_file_wav, format="wav")
        print("WAV文件导出成功!")
    except Exception as e:
        print(f"导出WAV失败: {str(e)}")

    # 尝试导出MP3 (可能失败如果没有ffmpeg)
    print(f"\n尝试导出MP3文件到: {output_file_mp3}")
    try:
        combined.export(output_file_mp3, format="mp3", bitrate="128k")
        print("MP3文件导出成功!")
    except Exception as e:
        print(f"导出MP3失败 (可能缺少ffmpeg): {str(e)}")
        print("请使用WAV文件,或安装ffmpeg后重试")

    # 计算总时长
    total_duration_ms = len(combined)
    total_duration_sec = total_duration_ms / 1000
    minutes = int(total_duration_sec // 60)
    seconds = int(total_duration_sec % 60)

    print("\n" + "="*60)
    print("合并完成!")
    if os.path.exists(output_file_wav):
        print(f"WAV文件: {output_file_wav}")
    if os.path.exists(output_file_mp3):
        print(f"MP3文件: {output_file_mp3}")
    print(f"总时长: {minutes}分{seconds}秒 ({total_duration_ms}ms)")
    print(f"成功处理: {success_count} 段音频")
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
        f.write(f"成功合并: {success_count}\n")
        f.write(f"失败数: {len(dialogues) - success_count}\n\n")

        if os.path.exists(output_file_wav):
            f.write(f"WAV文件: {output_file_wav}\n")
        if os.path.exists(output_file_mp3):
            f.write(f"MP3文件: {output_file_mp3}\n")
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
else:
    print("\n错误: 没有成功处理任何音频文件!")

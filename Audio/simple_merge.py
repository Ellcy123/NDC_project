import os

# 简单的二进制文件连接(仅适用于相同格式的MP3文件)
temp_dir = r"D:\NDC_project\Audio\temp_opening"
output_file = r"D:\NDC_project\Audio\Loop1_Opening_Full.mp3"

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

print(f"\n合并完成!文件保存到: {output_file}")
print("\n警告: 由于使用了简单的二进制连接,合成的音频可能有问题。")
print("建议安装ffmpeg后使用专业工具合并。")
print("\n安装ffmpeg: https://ffmpeg.org/download.html")

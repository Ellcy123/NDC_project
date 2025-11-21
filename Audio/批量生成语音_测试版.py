"""
NDC 语音批量生成脚本 - 测试版
用于测试 scene1_tommy_dialogues.json 的13句对话生成
"""

import json
import os
import time
from datetime import datetime

# ===== 配置区域 =====
CONFIG_FILE = r"D:\NDC_project\第一章内容（对话修正版）\scene1_tommy_dialogues.json"
OUTPUT_DIR = r"D:\NDC_project\Audio\Voice\Episode1\Loop1\Tommy"
LOG_FILE = r"D:\NDC_project\Audio\generation_log.txt"

# ===== 函数定义 =====

def load_config(config_path):
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def log_message(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    print(log_entry.strip())

    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry)

def generate_single_voice(dialogue, index):
    """
    生成单句语音

    注意: 这是示例代码,需要在Claude Code中使用MCP工具实际调用

    实际使用时需要调用:
    mcp__elevenlabs__text_to_speech(
        text=dialogue['text'],
        voice_name=dialogue['voice_name'],
        ...
    )
    """
    log_message(f"正在生成第 {index+1} 句: {dialogue['id']}")
    log_message(f"  角色: {dialogue['character']}")
    log_message(f"  文本: {dialogue['text'][:30]}...")
    log_message(f"  声音: {dialogue['voice_name']}")
    log_message(f"  情绪: {dialogue['emotion_note']}")

    # 这里需要实际调用 ElevenLabs MCP 工具
    # 返回生成的文件名
    return f"tts_sample_{index}.mp3"

def get_expected_filename(dialogue, index):
    """
    根据对话配置生成期望的文件名
    格式: {角色}_{序号}.mp3
    """
    character = dialogue['character']
    # 使用6位序号
    sequence = f"{index+1:06d}"
    return f"{character}_{sequence}.mp3"

def rename_files_in_order(output_dir, config):
    """
    按时间顺序重命名文件
    """
    log_message("\n===== 开始重命名文件 =====")

    # 获取目录中所有mp3文件,按修改时间排序
    files = []
    for filename in os.listdir(output_dir):
        if filename.endswith('.mp3'):
            filepath = os.path.join(output_dir, filename)
            mtime = os.path.getmtime(filepath)
            files.append((filename, filepath, mtime))

    # 按时间排序
    files.sort(key=lambda x: x[2])

    log_message(f"找到 {len(files)} 个音频文件")

    # 重命名
    renamed_count = 0
    for i, (old_name, old_path, _) in enumerate(files):
        if i < len(config):
            new_name = get_expected_filename(config[i], i)
            new_path = os.path.join(output_dir, new_name)

            # 如果已经是正确名称,跳过
            if old_name == new_name:
                log_message(f"  [{i+1}] 跳过 (已是正确名称): {new_name}")
                continue

            # 重命名
            try:
                os.rename(old_path, new_path)
                log_message(f"  [{i+1}] ✅ {old_name} → {new_name}")
                renamed_count += 1
            except Exception as e:
                log_message(f"  [{i+1}] ❌ 重命名失败: {e}")
        else:
            log_message(f"  [{i+1}] ⚠️  配置不足,跳过: {old_name}")

    log_message(f"\n重命名完成: {renamed_count}/{len(files)} 个文件")
    return renamed_count

def main():
    """主函数"""
    log_message("=" * 60)
    log_message("NDC 语音批量生成 - 测试开始")
    log_message("=" * 60)

    # 1. 加载配置
    log_message("\n步骤1: 加载配置文件")
    try:
        config = load_config(CONFIG_FILE)
        log_message(f"  ✅ 配置加载成功: {len(config)} 句对话")
    except Exception as e:
        log_message(f"  ❌ 配置加载失败: {e}")
        return

    # 2. 检查输出目录
    log_message("\n步骤2: 检查输出目录")
    if not os.path.exists(OUTPUT_DIR):
        log_message(f"  ⚠️  目录不存在,正在创建: {OUTPUT_DIR}")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    log_message(f"  ✅ 输出目录就绪")

    # 3. 显示生成计划
    log_message("\n步骤3: 生成计划")
    log_message(f"  总对话数: {len(config)}")
    log_message(f"  角色分布:")

    character_count = {}
    for dialogue in config:
        char = dialogue['character']
        character_count[char] = character_count.get(char, 0) + 1

    for char, count in character_count.items():
        log_message(f"    - {char}: {count}句")

    # 4. 批量生成 (这里只显示信息,实际需要手动调用MCP)
    log_message("\n步骤4: 语音生成")
    log_message("  ⚠️  注意: 需要手动使用 ElevenLabs MCP 工具生成")
    log_message("  每生成一句后,可以运行此脚本的重命名功能")

    # 显示前3句的生成命令
    log_message("\n  前3句生成命令示例:")
    for i in range(min(3, len(config))):
        dialogue = config[i]
        log_message(f"\n  --- 第{i+1}句 ---")
        log_message(f"  text: {dialogue['text'][:50]}...")
        log_message(f"  voice_name: {dialogue['voice_name']}")
        log_message(f"  language: {dialogue['language']}")
        log_message(f"  stability: {dialogue['stability']}")
        log_message(f"  speed: {dialogue['speed']}")

    # 5. 询问是否重命名
    log_message("\n步骤5: 文件重命名")
    log_message("  如果您已经生成了一些文件,可以运行重命名功能")

    # 显示期望的文件名
    log_message("\n  期望的文件名列表:")
    for i, dialogue in enumerate(config):
        expected_name = get_expected_filename(dialogue, i)
        log_message(f"    {i+1:2d}. {expected_name} - {dialogue['emotion_note']}")

    log_message("\n" + "=" * 60)
    log_message("测试脚本运行完成")
    log_message("=" * 60)

def rename_only():
    """仅执行重命名功能"""
    log_message("\n" + "=" * 60)
    log_message("执行文件重命名")
    log_message("=" * 60)

    try:
        config = load_config(CONFIG_FILE)
        renamed = rename_files_in_order(OUTPUT_DIR, config)
        log_message(f"\n✅ 重命名完成: {renamed} 个文件")
    except Exception as e:
        log_message(f"\n❌ 重命名失败: {e}")

# ===== 主程序入口 =====
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--rename":
        # 仅重命名模式
        rename_only()
    else:
        # 完整测试模式
        main()

# ===== 使用说明 =====
"""
使用方法:

1. 查看生成计划:
   python 批量生成语音_测试版.py

2. 生成语音 (手动使用 MCP 工具):
   - 参考脚本输出的命令
   - 在 Claude Code 中逐句调用 mcp__elevenlabs__text_to_speech

3. 重命名已生成的文件:
   python 批量生成语音_测试版.py --rename

4. 查看日志:
   查看 generation_log.txt
"""

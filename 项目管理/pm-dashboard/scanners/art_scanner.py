"""
美术资源扫描器 - 各类美术资源计数与覆盖率
"""
import os
import glob
from .config import UNITY_ART, UNITY_RESOURCES


def count_art_files(directory, extensions=None):
    """计数目录下的美术资源文件（排除 .meta 文件）"""
    if not os.path.isdir(directory):
        return 0
    if extensions is None:
        extensions = {".png", ".jpg", ".jpeg", ".psd", ".tga", ".bmp", ".gif", ".webp", ".svg"}

    count = 0
    for f in os.listdir(directory):
        full = os.path.join(directory, f)
        if os.path.isfile(full):
            ext = os.path.splitext(f)[1].lower()
            if ext in extensions or ext not in {".meta", ".ds_store"}:
                count += 1
    return count


def count_recursive(directory):
    """递归计数所有非 .meta 文件"""
    if not os.path.isdir(directory):
        return 0
    count = 0
    for root, dirs, files in os.walk(directory):
        for f in files:
            if not f.endswith(".meta") and not f.startswith("."):
                count += 1
    return count


def scan_by_subdirs(directory):
    """扫描目录下每个子目录的文件数"""
    result = {}
    if not os.path.isdir(directory):
        return result
    for entry in sorted(os.listdir(directory)):
        sub = os.path.join(directory, entry)
        if os.path.isdir(sub):
            result[entry] = count_recursive(sub)
    # 也计算根目录下的文件
    root_files = sum(1 for f in os.listdir(directory)
                     if os.path.isfile(os.path.join(directory, f))
                     and not f.endswith(".meta") and not f.startswith("."))
    if root_files > 0:
        result["_root"] = root_files
    return result


def scan_scene():
    """扫描场景背景资源"""
    scene_dir = os.path.join(UNITY_ART, "Scene")
    by_subdir = scan_by_subdirs(scene_dir)
    return {
        "total": sum(by_subdir.values()),
        "by_category": by_subdir,
    }


def scan_npc():
    """扫描 NPC 资源"""
    npc_dir = os.path.join(UNITY_ART, "NPC")
    by_subdir = scan_by_subdirs(npc_dir)
    return {
        "total": sum(by_subdir.values()),
        "by_category": by_subdir,
    }


def scan_movieclip():
    """扫描 MovieClip 动画资源"""
    mc_dir = os.path.join(UNITY_ART, "MovieClip")
    by_epi = scan_by_subdirs(mc_dir)
    return {
        "total": sum(by_epi.values()),
        "by_episode": by_epi,
    }


def scan_avg_clip():
    """扫描 AVG 对话演出资源"""
    avg_dir = os.path.join(UNITY_ART, "avg_clip")
    by_epi = scan_by_subdirs(avg_dir)
    return {
        "total": sum(by_epi.values()),
        "by_episode": by_epi,
    }


def scan_ui():
    """扫描 UI 资源"""
    ui_dir = os.path.join(UNITY_ART, "UI")
    return {"total": count_recursive(ui_dir)}


def scan_audio():
    """扫描音频资源"""
    audio_dir = os.path.join(UNITY_RESOURCES, "Audio")
    result = {"bgm": 0, "voice": 0, "sfx": 0}
    if not os.path.isdir(audio_dir):
        return result

    bgm_dir = os.path.join(audio_dir, "BGM")
    talk_dir = os.path.join(audio_dir, "Talk")
    sfx_dir = os.path.join(audio_dir, "buttonSFX")

    result["bgm"] = count_recursive(bgm_dir)
    result["voice"] = count_recursive(talk_dir)
    result["sfx"] = count_recursive(sfx_dir)
    return result


def calculate_coverage(design_data, art_data):
    """计算美术资源覆盖率（需要设计数据做分母）"""
    coverage = {}

    # MovieClip 覆盖率：3 个 EPI 中有几个有内容
    mc_episodes = art_data.get("movieclip", {}).get("by_episode", {})
    mc_with_content = sum(1 for v in mc_episodes.values() if v > 0)
    coverage["movieclip"] = f"{mc_with_content}/3 episodes"

    # avg_clip 覆盖率
    avg_episodes = art_data.get("avg_clip", {}).get("by_episode", {})
    avg_with_content = sum(1 for v in avg_episodes.values() if v > 0)
    coverage["avg_clip"] = f"{avg_with_content}/3 episodes"

    # 语音覆盖率
    coverage["voice"] = "0%" if art_data.get("audio", {}).get("voice", 0) == 0 else "有内容"

    return coverage


def run(design_data=None):
    """执行完整美术扫描"""
    result = {
        "scene": scan_scene(),
        "npc": scan_npc(),
        "movieclip": scan_movieclip(),
        "avg_clip": scan_avg_clip(),
        "ui": scan_ui(),
        "audio": scan_audio(),
    }

    # 计算覆盖率
    result["coverage"] = calculate_coverage(design_data or {}, result)

    # 总计
    result["total_files"] = sum([
        result["scene"]["total"],
        result["npc"]["total"],
        result["movieclip"]["total"],
        result["avg_clip"]["total"],
        result["ui"]["total"],
    ])

    return result

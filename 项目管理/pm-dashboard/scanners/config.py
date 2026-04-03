"""
PM Dashboard 配置文件
路径常量 + Supabase 凭据
"""
import os

# ============================================
# Supabase 配置
# ============================================
SUPABASE_URL = "https://tyqsamueendpanbfousp.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR5cXNhbXVlZW5kcGFuYmZvdXNwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzUxOTI1NjMsImV4cCI6MjA5MDc2ODU2M30.qa_EqkXHkq5ki8CYt0cJk-Se2vfj8PTVHci239YblfM"

# ============================================
# 项目路径
# ============================================
NDC_PROJECT = r"D:\NDC_project"
NDC_UNITY = r"D:\NDC"

# 设计文档
DESIGN_DIR = os.path.join(NDC_PROJECT, "剧情设计")
AVG_DIR = os.path.join(NDC_PROJECT, "AVG")
PREVIEW_DIR = os.path.join(NDC_PROJECT, "preview_new2", "data")

# Unity 工程
UNITY_XLS = os.path.join(NDC_UNITY, "res", "xls")           # XLSX 配置表源文件
UNITY_TABLE_JSON = os.path.join(NDC_UNITY, "Assets", "table")  # 生成的 JSON 配置表
UNITY_RESOURCES = os.path.join(NDC_UNITY, "Assets", "Resources")
UNITY_ART = os.path.join(UNITY_RESOURCES, "Art")
UNITY_SCRIPTS = os.path.join(NDC_UNITY, "Assets", "Scripts")

# ============================================
# 扫描规则
# ============================================
UNITS = ["Unit1", "Unit2", "Unit3"]
EPIS = ["EPI01", "EPI02", "EPI03"]
LOOPS = ["loop1", "loop2", "loop3", "loop4", "loop5", "loop6"]

# Unit ↔ EPI 映射
UNIT_TO_EPI = {"Unit1": "EPI01", "Unit2": "EPI02", "Unit3": "EPI03"}
EPI_TO_UNIT = {v: k for k, v in UNIT_TO_EPI.items()}

# 美术子目录
ART_CATEGORIES = {
    "scene": os.path.join(UNITY_ART, "Scene"),
    "npc": os.path.join(UNITY_ART, "NPC"),
    "movieclip": os.path.join(UNITY_ART, "MovieClip"),
    "avg_clip": os.path.join(UNITY_ART, "avg_clip"),
    "ui": os.path.join(UNITY_ART, "UI"),
    "video": os.path.join(UNITY_ART, "Video"),
    "3d": os.path.join(UNITY_ART, "3D"),
}

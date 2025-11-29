# -*- coding: utf-8 -*-
"""
从Testimony.yaml生成Testimony表Excel
按照Testimony表配置规则.md格式
"""

import yaml
import pandas as pd
from pathlib import Path

# 路径配置
INPUT_FILE = Path(r"D:\NDC_project\story\Testimony.yaml")
OUTPUT_FILE = Path(r"D:\NDC_project\story\Testimony_new.xlsx")

def load_yaml(file_path):
    """加载YAML文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def convert_testimony():
    """
    转换证词数据到Excel格式
    按照Testimony表配置规则.md的字段：
    id, speakerName, speakerNameEn, cnWords, enWords,
    ifIgnore, ifEvidence, cnExracted, enExracted
    """
    data = load_yaml(INPUT_FILE)

    rows = []
    for item in data:
        row = {
            'id': item.get('id', ''),
            'speakerName': item.get('speakerName', ''),
            'speakerNameEn': item.get('speakerNameEn', ''),
            'cnWords': item.get('cnWords', ''),
            'enWords': item.get('enWords', ''),
            'ifIgnore': item.get('ifIgnore', 0),
            'ifEvidence': item.get('ifEvidence', 0),
            'cnExracted': item.get('cnExracted', ''),
            'enExracted': item.get('enExracted', ''),
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    # 按照配置表规则的字段顺序
    columns_order = ['id', 'speakerName', 'speakerNameEn',
                     'cnWords', 'enWords',
                     'ifIgnore', 'ifEvidence',
                     'cnExracted', 'enExracted']
    df = df[columns_order]

    df.to_excel(OUTPUT_FILE, index=False)
    print(f"已生成: {OUTPUT_FILE}")
    print(f"  - 共 {len(rows)} 条证词数据")
    return df

def main():
    print("=" * 50)
    print("Testimony.yaml -> Excel 转换工具")
    print("=" * 50)

    convert_testimony()

    print("\n转换完成！")

if __name__ == "__main__":
    main()

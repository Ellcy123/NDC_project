# -*- coding: utf-8 -*-
"""
将story目录下的yaml配置文件转换为Excel并替换正式配置表
保留原有Excel的表头格式（类型行、说明行）
"""

import yaml
import pandas as pd
from pathlib import Path

# 路径配置
YAML_DIR = Path(r"D:\NDC_project\story")
OUTPUT_DIR = Path(r"D:\NDC\Config\Datas\story")

def load_yaml(file_path):
    """加载YAML文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def convert_npc():
    """转换NPCStaticData.yaml到Excel，保留原有表头"""
    yaml_path = YAML_DIR / "NPCStaticData.yaml"
    output_path = OUTPUT_DIR / "NPCStaticData.xlsx"

    # 读取原有Excel获取表头格式
    try:
        original_df = pd.read_excel(output_path, header=None)
        # 获取前两行作为表头（字段名 + 类型/说明行）
        header_rows = original_df.iloc[:2] if len(original_df) > 2 else None
        original_columns = original_df.iloc[0].tolist()
    except Exception as e:
        print(f"无法读取原有Excel: {e}")
        header_rows = None
        original_columns = None

    # 读取YAML数据
    data = load_yaml(yaml_path)
    df_data = pd.DataFrame(data)

    # 如果有原始表头，按原始列顺序重排数据
    if original_columns:
        # 确保所有原始列都存在（缺失的填空）
        for col in original_columns:
            if col not in df_data.columns:
                df_data[col] = ''

        # 按原始顺序排列列
        df_data = df_data.reindex(columns=original_columns)

    # 合并表头和数据
    if header_rows is not None:
        # 将数据添加到表头后面
        result_df = pd.concat([header_rows, df_data], ignore_index=True)
    else:
        result_df = df_data

    # 写入Excel（不带pandas默认表头）
    result_df.to_excel(output_path, index=False, header=False)
    print(f"已替换: {output_path}")
    print(f"  - 共 {len(data)} 条NPC数据")
    if header_rows is not None:
        print(f"  - 保留了原有表头格式（{len(header_rows)}行）")
    return result_df

def main():
    print("=" * 50)
    print("YAML -> Excel 转换并替换正式配置表")
    print("=" * 50)

    convert_npc()

    print("\n替换完成！")

if __name__ == "__main__":
    main()

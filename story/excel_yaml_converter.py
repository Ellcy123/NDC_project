"""
Excel <-> YAML 双向转换工具
支持 NDC 项目的数据表格转换
"""
import pandas as pd
import yaml
from pathlib import Path

# 确保yaml输出中文不转义
yaml.add_representer(str, lambda dumper, data: dumper.represent_scalar('tag:yaml.org,2002:str', data))

def excel_to_yaml(excel_path, yaml_path=None, sheet_name=0):
    """将Excel转换为YAML"""
    df = pd.read_excel(excel_path, sheet_name=sheet_name)

    # 跳过前两行（类型定义和注释）
    df = df.iloc[2:].reset_index(drop=True)

    # 清理列名
    df.columns = [str(c).strip() for c in df.columns]

    # 移除全为空的行
    df = df.dropna(how='all')

    # 转换为字典列表
    records = []
    for _, row in df.iterrows():
        record = {}
        for col in df.columns:
            val = row[col]
            # 跳过空值和##开头的列
            if pd.notna(val) and not str(col).startswith('##'):
                # 数值类型处理
                if isinstance(val, float) and val.is_integer():
                    val = int(val)
                record[col] = val
        if record:  # 只添加非空记录
            records.append(record)

    # 输出路径
    if yaml_path is None:
        yaml_path = Path(excel_path).with_suffix('.yaml')

    # 写入YAML
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(records, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    print(f"[OK] Converted: {excel_path} -> {yaml_path}")
    return yaml_path


def yaml_to_excel(yaml_path, excel_path=None):
    """将YAML转换回Excel"""
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    df = pd.DataFrame(data)

    if excel_path is None:
        excel_path = Path(yaml_path).with_suffix('.xlsx')

    df.to_excel(excel_path, index=False)
    print(f"[OK] Converted: {yaml_path} -> {excel_path}")
    return excel_path


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("用法: python excel_yaml_converter.py <文件路径>")
        print("  .xlsx -> .yaml")
        print("  .yaml -> .xlsx")
        sys.exit(1)

    file_path = sys.argv[1]

    if file_path.endswith('.xlsx'):
        excel_to_yaml(file_path)
    elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
        yaml_to_excel(file_path)
    else:
        print("[ERROR] Unsupported file format")

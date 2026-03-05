#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查AVG对话文件中的废弃ID（孤岛ID）
废弃ID定义：存在于文件中，但没有任何next字段指向它，且不是起始ID
"""

import json
import os
import glob

def analyze_dialogue_file(filepath):
    """分析单个对话文件，返回废弃ID列表"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not data:
        return []

    # 收集所有ID
    all_ids = set()
    for node in data:
        all_ids.add(node['id'])

    # 收集所有被引用的ID
    referenced_ids = set()
    for node in data:
        # 从next字段收集
        next_val = node.get('next', '')
        if next_val:
            # next可能是单个ID或多个ID用/分隔
            for next_id in str(next_val).split('/'):
                next_id = next_id.strip()
                if next_id:
                    try:
                        referenced_ids.add(int(next_id))
                    except ValueError:
                        pass

        # 从ParameterInt字段收集（分支跳转目标）
        for i in range(4):
            param_key = f'ParameterInt{i}'
            if param_key in node:
                param_val = node[param_key]
                if param_val and param_val != 0:
                    referenced_ids.add(int(param_val))

    # 起始ID是第一个节点的ID
    starting_id = data[0]['id']

    # 废弃ID = 所有ID - 被引用的ID - 起始ID
    orphaned_ids = all_ids - referenced_ids - {starting_id}

    return sorted(list(orphaned_ids))

def main():
    talk_dir = r'D:\NDC\NDC_project\AVG\Talk'

    # 获取所有JSON文件
    all_files = []
    for loop_dir in ['loop1', 'loop2', 'loop3', 'loop4', 'loop5', 'loop6']:
        pattern = os.path.join(talk_dir, loop_dir, '*.json')
        all_files.extend(glob.glob(pattern))

    all_files.sort()

    print(f"共找到 {len(all_files)} 个对话文件\n")
    print("=" * 60)

    files_with_orphans = []

    for filepath in all_files:
        rel_path = os.path.relpath(filepath, talk_dir)
        orphaned = analyze_dialogue_file(filepath)

        if orphaned:
            files_with_orphans.append((rel_path, orphaned))
            print(f"\n[有废弃ID] {rel_path}")
            print(f"  废弃ID: {orphaned}")

    print("\n" + "=" * 60)
    print(f"\n检查完成！")
    print(f"共检查 {len(all_files)} 个文件")
    print(f"发现 {len(files_with_orphans)} 个文件含有废弃ID")

    if files_with_orphans:
        print("\n含有废弃ID的文件汇总：")
        for rel_path, orphaned in files_with_orphans:
            print(f"  - {rel_path}: {orphaned}")

if __name__ == '__main__':
    main()

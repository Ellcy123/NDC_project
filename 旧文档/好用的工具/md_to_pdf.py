#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MD转PDF工具 - 将Markdown文件转换为PDF
用法: py md_to_pdf.py <md文件路径> [输出pdf路径]
"""

import sys
import os
import io
from pathlib import Path
from markdown_pdf import MarkdownPdf, Section

# 修复Windows控制台编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def convert_md_to_pdf(md_path, pdf_path=None):
    """将MD文件转换为PDF"""
    md_path = Path(md_path)

    if not md_path.exists():
        print(f"错误: 文件不存在 - {md_path}")
        return False

    # 如果没有指定输出路径，使用同名PDF
    if pdf_path is None:
        pdf_path = md_path.with_suffix('.pdf')
    else:
        pdf_path = Path(pdf_path)

    try:
        # 读取MD内容
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # 创建PDF转换器
        pdf = MarkdownPdf(toc_level=3)

        # 添加内容，设置工作目录为MD文件所在目录（用于处理相对路径的图片等）
        section = Section(md_content, root=str(md_path.parent))
        pdf.add_section(section)

        # 保存PDF
        pdf.save(str(pdf_path))

        print(f"✓ 转换成功: {md_path.name} -> {pdf_path.name}")
        return True

    except Exception as e:
        print(f"✗ 转换失败: {md_path.name} - {e}")
        return False

def batch_convert(folder_path, pattern="*.md"):
    """批量转换文件夹中的MD文件"""
    folder = Path(folder_path)
    md_files = list(folder.glob(pattern))

    if not md_files:
        print(f"未找到匹配的MD文件: {folder}/{pattern}")
        return

    print(f"找到 {len(md_files)} 个MD文件，开始转换...")
    print("-" * 50)

    success_count = 0
    for md_file in md_files:
        if convert_md_to_pdf(md_file):
            success_count += 1

    print("-" * 50)
    print(f"转换完成: {success_count}/{len(md_files)} 成功")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  单文件: py md_to_pdf.py <md文件路径> [输出pdf路径]")
        print("  批量:   py md_to_pdf.py --batch <文件夹路径>")
        sys.exit(1)

    if sys.argv[1] == "--batch":
        folder = sys.argv[2] if len(sys.argv) > 2 else "."
        batch_convert(folder)
    else:
        md_path = sys.argv[1]
        pdf_path = sys.argv[2] if len(sys.argv) > 2 else None
        convert_md_to_pdf(md_path, pdf_path)

#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Corrupter - An elegant file corruption simulator in Python.
#
# Copyright (c) 2025 DEXTRO Inc.
# All rights reserved.
#
# Author: DEXTRO Inc.
# Version: 1.0.0
# ----------------------------------------------------------------------------

import argparse
import os
import random
import sys

def print_custom_help():
    """ 打印帮助信息。 """
    app_name = os.path.basename(sys.argv[0])
    param_col_width = 15
    option_col_width = 28

    help_text = f"""
Corrupter - 一个简洁而强大的文件损坏模拟器。

用法: {app_name} <输入文件> [输出文件] [选项]

参数:
  {'<输入文件>'.ljust(param_col_width)}要损坏的源文件路径。
  {'[输出文件]'.ljust(param_col_width)}输出文件路径。如果省略，将自动生成。

选项:
  {'-h, --help'.ljust(option_col_width)}显示此帮助信息。
  {'-p, --probability <值>'.ljust(option_col_width)}设置每个字节的损坏概率（例如：0.001 代表 0.1%%）
  {''.ljust(option_col_width+2)}默认值：0.00001
  {'-b, --bitflip'.ljust(option_col_width)}设置损坏方式为随机翻转字节中的一个比特位。

Copyright (c) 2025 DEXTRO Inc. All rights reserved.
"""
    print(help_text.strip())
    sys.exit(0)


def corrupt_file(input_path, output_path, probability, use_bitflip):
    """
    Reads a file chunk by chunk, corrupts it based on the given parameters,
    and writes to the output file.
    """
    mode_str = 'bitflip' if use_bitflip else 'replace'
    
    print(f"--- 文件损坏任务 (Corrupter v1.0.0 by DEXTRO Inc.) ---")
    print(f"输入文件: {input_path}")
    print(f"输出文件: {output_path}")
    print(f"损坏模式: {mode_str}")
    print(f"损坏概率: {probability * 100:.5f}%")
    print("-----------------------------------------------------------\n")

    BUFFER_SIZE = 4 * 1024 * 1024
    processed_bytes = 0
    corrupted_bytes = 0
    
    try:
        total_size = os.path.getsize(input_path)
    except FileNotFoundError:
        print(f"错误: 输入文件未找到 '{input_path}'", file=sys.stderr)
        return

    try:
        with open(input_path, 'rb') as fin, open(output_path, 'wb') as fout:
            while True:
                chunk = fin.read(BUFFER_SIZE)
                if not chunk:
                    break
                
                mutable_chunk = bytearray(chunk)

                for i in range(len(mutable_chunk)):
                    if random.random() < probability:
                        corrupted_bytes += 1
                        if use_bitflip:
                            bit_to_flip = random.randint(0, 7)
                            mutable_chunk[i] ^= (1 << bit_to_flip)
                        else:
                            mutable_chunk[i] = random.randint(0, 255)
                
                fout.write(mutable_chunk)
                processed_bytes += len(chunk)
                
                percentage = (processed_bytes / total_size * 100) if total_size > 0 else 100
                print(f"\r进度: {percentage:.2f}% [{processed_bytes} / {total_size} bytes]", end="")
                sys.stdout.flush()

        print("\n\n--- 任务完成 ---")
        actual_rate = (corrupted_bytes / processed_bytes * 100) if processed_bytes > 0 else 0
        print(f"总字节数: {processed_bytes}")
        print(f"损坏字节数: {corrupted_bytes}")
        print(f"实际损坏率: {actual_rate:.5f}%")
        print("------------------")

    except IOError as e:
        print(f"\n错误: 文件读写失败 - {e}", file=sys.stderr)


def main():
    """
    解析命令行参数并启动损坏过程。
    """
    if '-h' in sys.argv or '--help' in sys.argv:
        print_custom_help()
    
    # 自动提示
    if len(sys.argv) < 2:
        app_name = os.path.basename(sys.argv[0])
        print(f"用法: {app_name} <输入文件> [输出文件] [选项]", file=sys.stderr)
        print(f"使用 '{app_name} -h' 查看完整帮助信息。", file=sys.stderr)
        sys.exit(1)
        
    parser = argparse.ArgumentParser(add_help=False)
    
    parser.add_argument("input_file")
    parser.add_argument("output_file", nargs='?', default=None)
    parser.add_argument("-p", "--probability", type=float, default=0.00001)
    parser.add_argument("-b", "--bitflip", action="store_true")
    
    try:
        # 只解析已知的参数，忽略其他
        args, unknown = parser.parse_known_args()
        if unknown:
            # 检查是否有除了-h/--help之外的未知参数
            is_truly_unknown = any(arg not in ['-h', '--help'] for arg in unknown)
            if is_truly_unknown:
                print(f"错误: 发现未知参数: {' '.join(unknown)}", file=sys.stderr)
                sys.exit(1)

    except SystemExit:
        return

    output_path = args.output_file
    if not output_path:
        base, ext = os.path.splitext(args.input_file)
        output_path = f"{base}_corrupted{ext}"
        
    if os.path.abspath(args.input_file) == os.path.abspath(output_path):
        print("错误: 输入文件和输出文件不能是同一个文件! 这会破坏源文件。", file=sys.stderr)
        sys.exit(1)
        
    corrupt_file(args.input_file, output_path, args.probability, args.bitflip)


if __name__ == "__main__":
    main()
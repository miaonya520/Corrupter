#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Corrupter - An elegant file corruption simulator in Python.
#
# Copyright (c) 2025 DEXTRO Inc.
# All rights reserved.
#
# Author: DEXTRO Inc.
# Version: 1.1.0
# ----------------------------------------------------------------------------

import argparse
import os
import random
import sys

def corrupt_file(input_path, output_path, probability, mode, burst_length, seed):
    """
    Reads a file chunk by chunk, corrupts it based on the given parameters,
    and writes to the output file.
    """
    print(f"--- 文件损坏任务 (Corrupter v1.1.0 by DEXTRO Inc.) ---")
    print(f"输入文件: {input_path}")
    print(f"输出文件: {output_path}")
    print(f"损坏模式: {mode}")
    print(f"损坏概率: {probability * 100:.5f}%")
    if mode == 'burst':
        print(f"撕裂长度: {burst_length}")
    if seed is not None:
        print(f"随机种子: {seed}")
    print("-----------------------------------------------------------\n")

    BUFFER_SIZE = 4 * 1024 * 1024  # 4MB buffer
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
                
                i = 0
                while i < len(mutable_chunk):
                    if random.random() < probability:
                        if mode == 'burst':
                            # Burst 模式: 连续损坏 N 个字节
                            for j in range(burst_length):
                                current_pos = i + j
                                if current_pos < len(mutable_chunk):
                                    mutable_chunk[current_pos] = random.randint(0, 255)
                                    corrupted_bytes += 1
                            i += burst_length  # 跳过已损坏的字节
                            continue

                        # 其他单字节模式
                        corrupted_bytes += 1
                        if mode == 'bitflip':
                            # 比特翻转模式
                            bit_to_flip = random.randint(0, 7)
                            mutable_chunk[i] ^= (1 << bit_to_flip)
                        elif mode == 'zero':
                            # 置零模式
                            mutable_chunk[i] = 0
                        else:  # 'replace' 模式
                            mutable_chunk[i] = random.randint(0, 255)
                    
                    i += 1  # 移动到下一个字节
                
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
    # 使用 argparse 的 formatter_class 来更好地控制帮助文本格式
    # RawTextHelpFormatter 会保留换行符和空格
    parser = argparse.ArgumentParser(
        description="Corrupter - 一个简洁而强大的文件损坏模拟器。",
        epilog="Copyright (c) 2025 DEXTRO Inc. All rights reserved.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # 位置参数
    parser.add_argument("input_file", help="要损坏的源文件路径。")
    parser.add_argument("output_file", nargs='?', default=None,
                        help="输出文件路径。如果省略，将基于输入文件名自动生成。")
    
    # 通用选项
    parser.add_argument("-p", "--probability", type=float, default=0.00001,
                        help="设置每个字节或每个撕裂事件的损坏概率 (例如: 0.001 代表 0.1%%)。\n默认值: %(default)s")
    parser.add_argument("-s", "--seed", type=int, default=None,
                        help="设置随机数生成器的种子，用于复现损坏结果。")

    # 损坏模式组，这些选项是互斥的
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("-b", "--bitflip", action="store_true",
                            help="翻转模式: 随机翻转字节中的一个比特位。")
    mode_group.add_argument("-z", "--zero", action="store_true",
                            help="置零模式: 随机将字节置为零。")
    mode_group.add_argument("--burst", type=int, metavar='N',
                            help="撕裂模式: 随机连续修改 N 个字节。")

    args = parser.parse_args()

    # 设置随机种子
    if args.seed is not None:
        random.seed(args.seed)

    # 确定损坏模式
    mode = 'replace' # 默认模式
    if args.bitflip:
        mode = 'bitflip'
    elif args.zero:
        mode = 'zero'
    elif args.burst is not None:
        if args.burst <= 0:
            print("错误: --burst 的值必须是一个正整数。", file=sys.stderr)
            sys.exit(1)
        mode = 'burst'

    # 自动生成输出文件名（如果未提供）
    output_path = args.output_file
    if not output_path:
        base, ext = os.path.splitext(args.input_file)
        output_path = f"{base}_corrupted{ext}"
        
    # 安全检查：防止覆盖源文件
    if os.path.abspath(args.input_file) == os.path.abspath(output_path):
        print("错误: 输入文件和输出文件不能是同一个文件! 这会破坏源文件。", file=sys.stderr)
        sys.exit(1)
        
    corrupt_file(args.input_file, output_path, args.probability, mode, args.burst, args.seed)


if __name__ == "__main__":
    main()
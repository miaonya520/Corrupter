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

def no_op(*args, **kwargs):
    """一个什么都不做的函数，用于静默模式。"""
    pass

def corrupt_stream(fin, fout, probability, mode, burst_length, seed, log_func=print):
    """
    从输入流中读取，逐块破坏，然后写入输出流。使用提供的日志函数进行输出。
    """
    # 当处理流时，我们不知道总大小，所以进度条需要调整
    is_stream = fin.isatty() or fout.isatty()
    total_size = 0
    if not is_stream:
        try:
            # 尝试获取文件大小以显示进度条
            fin.seek(0, os.SEEK_END)
            total_size = fin.tell()
            fin.seek(0)
        except (OSError, AttributeError):
            is_stream = True # 如果无法 seek，当作流处理
    
    log_func(f"--- 文件损坏任务 (Corrupter v1.1.0 by DEXTRO Inc.) ---")
    input_desc = getattr(fin, 'name', "标准输入 (stdin)")
    output_desc = getattr(fout, 'name', "标准输出 (stdout)")
    log_func(f"输入: {input_desc}")
    log_func(f"输出: {output_desc}")
    log_func(f"损坏模式: {mode}")
    log_func(f"目标字节损坏率: {probability * 100:.5f}%")

    trigger_probability = probability
    if mode == 'burst':
        if burst_length and burst_length > 0:
            trigger_probability = probability / burst_length
            log_func(f"撕裂长度: {burst_length}")
            log_func(f"内部触发概率: {trigger_probability * 100:.5f}% (目标损坏率 / 撕裂长度)")
        else:
            trigger_probability = 0
            log_func(f"撕裂长度: {burst_length} (无效, 将不执行损坏)")

    if seed is not None:
        log_func(f"随机种子: {seed}")
    
    if fout.isatty():
        log_func("-----------------------------------------------------------\n")

    if not (0.0 <= trigger_probability <= 1.0):
        # 错误/警告信息总是直接打印到 stderr，不通过 log_func
        print(f"警告: 计算出的内部触发概率 ({trigger_probability:.5f}) 超出 [0, 1] 范围。", file=sys.stderr)
        trigger_probability = max(0.0, min(1.0, trigger_probability))
        print(f"已将触发概率限制为: {trigger_probability:.5f}", file=sys.stderr)

    BUFFER_SIZE = 4 * 1024 * 1024
    processed_bytes = 0
    corrupted_bytes = 0
    
    try:
        while True:
            chunk = fin.read(BUFFER_SIZE)
            if not chunk:
                break
            
            mutable_chunk = bytearray(chunk)
            
            i = 0
            while i < len(mutable_chunk):
                if random.random() < trigger_probability:

                    if mode == 'burst':
                        for j in range(burst_length):
                            current_pos = i + j
                            if current_pos < len(mutable_chunk):
                                mutable_chunk[current_pos] = random.randint(0, 255)
                                corrupted_bytes += 1
                        i += burst_length
                        continue

                    corrupted_bytes += 1
                    if mode == 'bitflip':
                        mutable_chunk[i] ^= (1 << random.randint(0, 7))
                    elif mode == 'zero':
                        mutable_chunk[i] = 0
                    else:
                        mutable_chunk[i] = random.randint(0, 255)
                
                i += 1
            
            fout.write(mutable_chunk)
            processed_bytes += len(chunk)
            
            if total_size > 0 and fout.isatty():
                percentage = (processed_bytes / total_size * 100)
                print(f"\r进度: {percentage:.2f}% [{processed_bytes} / {total_size} bytes]", end="")
                sys.stdout.flush()

        if fout.isatty():
            log_func("\n\n--- 任务完成 ---")
            actual_rate = (corrupted_bytes / processed_bytes * 100) if processed_bytes > 0 else 0
            log_func(f"总字节数: {processed_bytes}")
            log_func(f"损坏字节数: {corrupted_bytes}")
            log_func(f"实际损坏率: {actual_rate:.5f}%")
            log_func("------------------")

    except (IOError, BrokenPipeError) as e:
        # 错误信息总是直接打印到 stderr
        print(f"\n错误: 流读写失败 - {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """
    解析命令行参数并启动损坏过程。
    """
    parser = argparse.ArgumentParser(
        description="Corrupter - 一个简洁而强大的文件损坏模拟器。支持标准输入/输出。",
        epilog="Copyright (c) 2025 DEXTRO Inc. All rights reserved.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument("input_file", help="要损坏的源文件路径。使用 '-' 从标准输入 (stdin) 读取。")
    parser.add_argument("output_file", nargs='?', default=None, help="输出文件路径。使用 '-' 写入标准输出 (stdout)。\n如果省略，将基于输入文件名自动生成。")
    parser.add_argument("-p", "--probability", type=float, default=0.00001, help="设置目标字节损坏率 (例如: 0.001 代表 0.1%%)。\n默认值: %(default)s")
    parser.add_argument("-s", "--seed", type=int, default=None, help="设置随机数生成器的种子，用于复现损坏结果。")
    parser.add_argument("-q", "--quiet", action="store_true", help="静默模式，不向 stderr 打印任何非错误信息。")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("-b", "--bitflip", action="store_true", help="翻转模式: 随机翻转字节中的一个比特位。")
    mode_group.add_argument("-z", "--zero", action="store_true", help="置零模式: 随机将字节修改为零。")
    mode_group.add_argument("--burst", type=int, metavar='N', help="撕裂模式: 随机连续修改 N 个字节。")

    args = parser.parse_args()

    # 根据 -q 参数决定使用哪个函数来打印日志
    if args.quiet:
        log_func = no_op  # 静默模式下，日志函数什么都不做
    else:
        # 正常模式下，日志函数将信息打印到标准错误流 (stderr)
        log_func = lambda *a, **kw: print(*a, file=sys.stderr, **kw)


    if args.seed is not None:
        random.seed(args.seed)

    mode = 'replace'
    if args.bitflip:
        mode = 'bitflip'
    elif args.zero:
        mode = 'zero'
    elif args.burst is not None:
        if args.burst <= 0:
            # 错误信息总是直接打印到 stderr
            print("错误: --burst 的值必须是一个正整数。", file=sys.stderr)
            sys.exit(1)
        mode = 'burst'

    input_path = args.input_file
    output_path = args.output_file

    if input_path == '-' and not output_path:
        print("错误: 从标准输入读取时，必须指定输出文件或使用 '-' 表示标准输出。", file=sys.stderr)
        sys.exit(1)

    if not output_path:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_corrupted{ext}"
        
    if input_path != '-' and output_path != '-' and os.path.abspath(input_path) == os.path.abspath(output_path):
        print("错误: 输入文件和输出文件不能是同一个文件!", file=sys.stderr)
        sys.exit(1)
        
    fin = sys.stdin.buffer if input_path == '-' else open(input_path, 'rb')
    fout = sys.stdout.buffer if output_path == '-' else open(output_path, 'wb')

    try:
        corrupt_stream(fin, fout, args.probability, mode, args.burst, args.seed, log_func=log_func)
    finally:
        if fin is not sys.stdin.buffer:
            fin.close()
        if fout is not sys.stdout.buffer:
            fout.close()

def cli_entry_point():
    """This function is the entry point for the command-line script."""
    try:
        main()
    except KeyboardInterrupt:
        print("\n操作被用户中断。", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    cli_entry_point()
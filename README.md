# Corrupter

**一个简洁而强大的文件损坏模拟器。**

Corrupter 是一个用 Python 编写的命令行工具，旨在精确、可复现地模拟各种文件损坏场景。无论您是需要测试数据的鲁棒性，还是想创造独特的“故障艺术”（Glitch Art），Corrupter 都能为您提供强大而灵活的支持。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()

## 核心特性

*   **多种损坏模式**:
    * 替换模式 (默认): 随机替换文件中的字节。
    * 翻转模式: 随机翻转字节中的一个比特位，进行更精细、更隐蔽的损坏。
    * 置零模式: 将字节随机置为零，模拟数据丢失。
    * 撕裂模式: 连续损坏多个字节，模拟物理介质划痕或数据块传输错误。
*   **精确损坏控制**: 可精确设置每个字节被损坏的概率。
*   **结果可复现**: 可设置种子以确保可复现每次损坏。
*   **流处理支持**: 完全支持 `stdin` 和 `stdout`，可无缝集成到命令行管道中。
*   **用户友好**: 实时进度条、任务总结报告和清晰的帮助信息。
*   **安全第一**: 绝不覆盖源文件，防止意外数据丢失。
*   **高效性能**: 即使是 GB 级的大文件也能轻松处理。
*   **零依赖**: 仅需 Python 3 标准库。
*   **经过单元测试**: 核心功能拥有全面的测试套件，保证了其稳定性和可靠性。

## 安装

您可以通过 `pip` 轻松安装 Corrupter：

```bash
pip install corrupter-1.1.0-py3-none-any.whl
```
安装完成后，`corrupter` 命令将立即可用。

**备选方法 (手动安装):**
如果您不想通过 `pip` 安装，也可以直接下载 `corrupter.py` 脚本，并使用 `python` 运行它。

## 使用方法

### 基本语法
```bash
corrupter [OPTIONS] <input_file> [output_file]
```

### 参数详解

#### 位置参数:
*   `input_file`: 要损坏的源文件路径。
    *   使用 **`-`** 从标准输入 (stdin) 读取。
*   `output_file` (可选): 输出文件路径。
    *   如果省略，将自动生成一个带 `_corrupted` 后缀的文件名。
    *   使用 **`-`** 写入标准输出 (stdout)。
    *   **注意**: 当输入为 stdin (`-`) 时，必须指定此参数。

#### 选项:
*   `-p, --probability <FLOAT>`: 设置目标字节损坏率（例如: `0.01` 代表 1%）。默认值: `0.00001`。
*   `-s, --seed <INTEGER>`: 设置随机数生成器的种子，用于复现结果。
*   `-q, --quiet`: 静默模式，不打印进度和总结信息。非常适合在脚本中使用。
*   `-h, --help`: 显示帮助信息并退出。

#### 损坏模式 (互斥选项):
*   `-b, --bitflip`: **翻转模式**：随机翻转字节中的一个比特位。
*   `-z, --zero`: **置零模式**：随机将字节置为零。
*   `--burst <N>`: **撕裂模式**：触发时，连续损坏 `N` 个字节。
*   如果未指定任何模式，将默认使用**替换模式**。

---

## 示例

#### 1. 基本损坏
损坏一个图片文件，自动生成输出文件名。
```bash
corrupter photo.jpg --probability 0.001
# 将会创建 photo_corrupted.jpg
```

#### 2. 创造故障艺术 (Glitch Art)
使用 `bitflip` 模式和固定的种子，对图片进行轻微、可复现的损坏。
```bash
corrupter artwork.png artwork_glitched.png -b -p 0.0005 --seed 1337
```

#### 3. 模拟磁盘划痕
使用 `burst` 模式，模拟一个 8KB 的连续数据块损坏。
```bash
# 目标损坏率为 5%，撕裂长度为 8192 字节
corrupter data.zip corrupted_data.zip --burst 8192 -p 0.05
```

#### 4. 使用管道进行流式处理
这是 Corrupter 最强大的功能之一。无需创建临时文件即可完成复杂任务。

**a) 损坏一个文件并通过管道传递给 `hexdump` 查看：**
```bash
corrupter my_program.exe - -b -p 0.01 | hexdump -C | head -n 20
```

**b) 从 `dd` 生成随机数据，损坏后保存到文件：**
```bash
# 生成 10MB 的随机数据，通过管道损坏后存盘
dd if=/dev/urandom bs=1M count=10 | corrupter - corrupted_random.dat -p 0.1
```

**c) 在自动化脚本中静默运行：**
```bash
#!/bin/bash
INPUT_FILE="archive.tar.gz"
CORRUPTED_FILE="test_archive.tar.gz"

echo "Creating corrupted archive for testing..."
# 使用 -q 选项，不会有任何非错误信息打印到控制台
corrupter "$INPUT_FILE" "$CORRUPTED_FILE" -q --burst 4096 -p 0.05 --seed 42

echo "Running recovery test on $CORRUPTED_FILE..."
# ./my_recovery_tool "$CORRUPTED_FILE"
```

## 开发与测试

本项目包含一个完整的单元测试套件，以确保核心功能的稳定性和正确性。

要克隆仓库并运行测试，请执行：
```bash
git clone https://github.com/miaonya520/corrupter.git
cd corrupter
python -m unittest tests/test_corrupter.py
```

## 版权与许可

~~Copyright (c) 2025 DEXTRO Inc. All rights reserved.~~（注：DEXTRO Inc.非真实公司，仅供娱乐，如有雷同，纯属巧合）

由 miaonya 制作。

本项目采用[MIT 许可证](https://opensource.org/licenses/MIT)授权。
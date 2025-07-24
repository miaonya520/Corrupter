# Corrupter - 一个简洁而强大的文件损坏模拟器。

用法: Corrupter.py <输入文件> \[输出文件] \[选项]

参数:
  <输入文件> 要损坏的源文件路径。
  \[输出文件] 输出文件路径。如果省略，将自动生成。

选项:
  -h, --help 显示此帮助信息。
  -p, --probability <值> 设置每个字节的损坏概率（例如：0.001 代表 0.1%%），默认值为 0.00001。
  -b, --bitflip 设置损坏方式为随机翻转字节中的一个比特位。

Copyright (c) 2025 DEXTRO Inc. All rights reserved.

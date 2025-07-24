# test_corrupter.py
import unittest
import io
import random
from corrupter import corrupt_stream, no_op

class TestCorrupter(unittest.TestCase):

    def setUp(self):
        """在每个测试方法运行前设置通用的测试数据。"""
        self.original_data = bytes(range(256)) * 40
        self.input_stream = io.BytesIO(self.original_data)
        self.output_stream = io.BytesIO()

    def test_probability_zero_no_corruption(self):
        """测试当概率为0时，文件内容完全不变。"""
        corrupt_stream(
            fin=self.input_stream,
            fout=self.output_stream,
            probability=0.0,
            mode='replace',
            burst_length=None,
            seed=42,
            log_func=no_op  # 在测试中我们不关心日志输出
        )
        self.assertEqual(self.output_stream.getvalue(), self.original_data)

    def test_probability_one_full_corruption_replace(self):
        """测试当概率为1时，文件内容完全被替换。"""
        corrupt_stream(
            fin=self.input_stream,
            fout=self.output_stream,
            probability=1.0,
            mode='replace',
            burst_length=None,
            seed=42,
            log_func=no_op
        )
        corrupted_data = self.output_stream.getvalue()
        self.assertEqual(len(corrupted_data), len(self.original_data))
        self.assertNotEqual(corrupted_data, self.original_data)

    def test_mode_zero_with_probability_one(self):
        """测试 zero 模式在概率为1时，所有字节都变为0。"""
        corrupt_stream(
            fin=self.input_stream,
            fout=self.output_stream,
            probability=1.0,
            mode='zero',
            burst_length=None,
            seed=42,
            log_func=no_op
        )
        corrupted_data = self.output_stream.getvalue()
        expected_data = b'\x00' * len(self.original_data)
        self.assertEqual(corrupted_data, expected_data)

    def test_mode_bitflip(self):
        """测试 bitflip 模式确实改变了数据。"""
        corrupt_stream(
            fin=self.input_stream,
            fout=self.output_stream,
            probability=0.1,
            mode='bitflip',
            burst_length=None,
            seed=42,
            log_func=no_op
        )
        corrupted_data = self.output_stream.getvalue()
        self.assertNotEqual(corrupted_data, self.original_data)
        diff_count = sum(1 for i in range(len(self.original_data)) if self.original_data[i] != corrupted_data[i])
        self.assertGreater(diff_count, 0)

    def test_seed_reproducibility(self):
        """测试使用相同的种子总能产生相同的结果。"""
        output1 = io.BytesIO()
        corrupt_stream(
            fin=io.BytesIO(self.original_data),
            fout=output1,
            probability=0.01,
            mode='replace',
            burst_length=None,
            seed=12345,
            log_func=no_op
        )
        
        output2 = io.BytesIO()
        corrupt_stream(
            fin=io.BytesIO(self.original_data),
            fout=output2,
            probability=0.01,
            mode='replace',
            burst_length=None,
            seed=12345,
            log_func=no_op
        )
        
        self.assertEqual(output1.getvalue(), output2.getvalue())

    def test_burst_mode_logic(self):
        """测试 burst 模式，并验证其损坏率是否符合预期。"""
        burst_length = 10
        target_probability = 0.1

        corrupt_stream(
            fin=self.input_stream,
            fout=self.output_stream,
            probability=target_probability,
            mode='burst',
            burst_length=burst_length,
            seed=42,
            log_func=no_op
        )
        corrupted_data = self.output_stream.getvalue()
        corrupted_bytes_count = sum(1 for i in range(len(self.original_data)) if self.original_data[i] != corrupted_data[i])
        actual_rate = corrupted_bytes_count / len(self.original_data)
        self.assertAlmostEqual(actual_rate, target_probability, delta=0.02)

    def test_empty_file(self):
        """测试当输入为空时，程序能正常工作且输出也为空。"""
        input_stream = io.BytesIO(b'')
        output_stream = io.BytesIO()
        corrupt_stream(
            fin=input_stream,
            fout=output_stream,
            probability=1.0,
            mode='replace',
            burst_length=None,
            seed=42,
            log_func=no_op
        )
        self.assertEqual(output_stream.getvalue(), b'')

if __name__ == '__main__':
    unittest.main(verbosity=2)

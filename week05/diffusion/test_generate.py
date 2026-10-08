"""Device checks only: no model downloads or image generation."""

import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = Path(__file__).with_name("generate.py")


class DeviceTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SOURCE.is_file(), "The runnable Diffusers example is missing")
        self.torch = importlib.import_module("torch")
        spec = importlib.util.spec_from_file_location("generate_example", SOURCE)
        self.example = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.example)

    def test_cpu_uses_full_precision(self):
        self.assertEqual(self.example.select_device("cpu"), ("cpu", self.torch.float32))

    def test_cuda_uses_half_precision(self):
        with patch.object(self.torch.cuda, "is_available", return_value=True):
            self.assertEqual(self.example.select_device("auto"), ("cuda", self.torch.float16))

    def test_apple_gpu_uses_full_precision(self):
        with patch.object(self.torch.cuda, "is_available", return_value=False), patch.object(self.torch.backends.mps, "is_available", return_value=True):
            self.assertEqual(self.example.select_device("auto"), ("mps", self.torch.float32))

    def test_no_accelerator_falls_back_to_full_precision_cpu(self):
        with patch.object(self.torch.cuda, "is_available", return_value=False), patch.object(self.torch.backends.mps, "is_available", return_value=False):
            self.assertEqual(self.example.select_device("auto"), ("cpu", self.torch.float32))

    def test_unavailable_cuda_is_rejected_before_loading_a_model(self):
        with patch.object(self.torch.cuda, "is_available", return_value=False):
            with self.assertRaises(RuntimeError):
                self.example.select_device("cuda")


if __name__ == "__main__":
    unittest.main()

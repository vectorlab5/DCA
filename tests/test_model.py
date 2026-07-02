import unittest
import torch
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.model import DCANet, DiffeomorphicSTN

class TestModel(unittest.TestCase):
    def setUp(self):
        self.batch_size = 2
        self.channels = 3
        self.height = 224
        self.width = 224
        self.num_classes = 9
        self.input_tensor = torch.randn(self.batch_size, self.channels, self.height, self.width)

    def test_stn_forward(self):
        stn = DiffeomorphicSTN()
        warped_x, phi, v = stn(self.input_tensor)
        
        print(f"STN Output Shapes - Warped: {warped_x.shape}, Phi: {phi.shape}, V: {v.shape}")
        
        self.assertEqual(warped_x.shape, self.input_tensor.shape)
        self.assertEqual(phi.shape, (self.batch_size, 2, self.height, self.width))
        self.assertEqual(v.shape, (self.batch_size, 2, self.height, self.width))

    def test_dcanet_forward(self):
        model = DCANet(num_classes=self.num_classes)
        logits, warped_x, phi, v = model(self.input_tensor)
        
        print(f"DCANet Output Shapes - Logits: {logits.shape}")
        
        self.assertEqual(logits.shape, (self.batch_size, self.num_classes))
        self.assertEqual(warped_x.shape, self.input_tensor.shape)

if __name__ == '__main__':
    unittest.main()

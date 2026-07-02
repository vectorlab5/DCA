import unittest
import torch
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.loss import ConformalLoss

class TestLoss(unittest.TestCase):
    def setUp(self):
        self.loss_fn = ConformalLoss()
        self.B, self.H, self.W = 2, 32, 32

    def test_identity_flow(self):
        # Identity flow: phi = 0
        phi = torch.zeros(self.B, 2, self.H, self.W)
        loss = self.loss_fn(phi)
        print(f"Identity Flow Loss: {loss.item()}")
        self.assertAlmostEqual(loss.item(), 0.0, places=5)

    def test_conformal_flow(self):
        # A simple conformal flow: translation or rotation
        # Let's try translation: u = c1, v = c2
        phi = torch.zeros(self.B, 2, self.H, self.W)
        phi[:, 0, :, :] = 0.1
        phi[:, 1, :, :] = 0.2
        loss = self.loss_fn(phi)
        print(f"Translation Flow Loss: {loss.item()}")
        self.assertAlmostEqual(loss.item(), 0.0, places=5)
        
    def test_non_conformal_flow(self):
        # Non-conformal flow: stretching in one direction only
        # u = x, v = 0
        # du/dx = 1, du/dy = 0
        # dv/dx = 0, dv/dy = 0
        # (du_dx - dv_dy)^2 + (du_dy + dv_dx)^2 = (1-0)^2 + (0+0)^2 = 1
        
        # Construct grid
        y, x = torch.meshgrid(torch.arange(self.H), torch.arange(self.W))
        phi = torch.zeros(self.B, 2, self.H, self.W)
        
        # Apply stretch in x: phi_x = 0.1 * x
        phi[:, 0, :, :] = 0.1 * x.float()
        
        loss = self.loss_fn(phi)
        print(f"Non-Conformal Flow Loss: {loss.item()}")
        self.assertGreater(loss.item(), 0.0)

if __name__ == '__main__':
    unittest.main()

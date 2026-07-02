import torch
import torch.nn as nn

class ConformalLoss(nn.Module):
    def __init__(self, weight=1.0):
        super(ConformalLoss, self).__init__()
        self.weight = weight

    def forward(self, phi):
        """
        Computes the Conformal Energy Loss.
        phi: (B, 2, H, W) - Deformation field (displacement or absolute coordinates?)
        The STN implementation returns 'phi' as the displacement field integrated from velocity.
        So the actual mapping is ID + phi.
        
        Let f(x, y) = (x + phi_x, y + phi_y).
        Jacobian J = [[1 + dphi_x/dx, dphi_x/dy],
                      [dphi_y/dx, 1 + dphi_y/dy]]
                      
        Conformal Energy E_C = ||J||_F^2 - 2 * det(J)
                             = (J_11^2 + J_12^2 + J_21^2 + J_22^2) - 2*(J_11*J_22 - J_12*J_21)
                             = (J_11 - J_22)^2 + (J_12 + J_21)^2
                             
        This is exactly the Cauchy-Riemann equations:
        u_x = v_y  => J_11 = J_22
        u_y = -v_x => J_12 = -J_21
        """
        
        # Compute gradients
        # phi is (B, 2, H, W)
        # We need to be careful with units. 
        # If phi is in [-1, 1] normalized coordinates, we should scale gradients or just minimize the quantity in that space.
        # Minimizing in normalized space is sufficient for enforcing the property.
        
        u = phi[:, 0, :, :] # x-displacement
        v = phi[:, 1, :, :] # y-displacement
        
        # Use central difference for gradients
        # u, v are (B, H, W)
        
        # du/dx: (B, H, W-2)
        du_dx = (u[:, :, 2:] - u[:, :, :-2]) / 2
        # du/dy: (B, H-2, W)
        du_dy = (u[:, 2:, :] - u[:, :-2, :]) / 2
        # dv/dx: (B, H, W-2)
        dv_dx = (v[:, :, 2:] - v[:, :, :-2]) / 2
        # dv/dy: (B, H-2, W)
        dv_dy = (v[:, 2:, :] - v[:, :-2, :]) / 2
        
        # Crop to common valid region (H-2, W-2)
        # du_dx is missing 2 pixels in W, so we crop 1 pixel from top and bottom in H
        du_dx = du_dx[:, 1:-1, :]
        # du_dy is missing 2 pixels in H, so we crop 1 pixel from left and right in W
        du_dy = du_dy[:, :, 1:-1]
        
        dv_dx = dv_dx[:, 1:-1, :]
        dv_dy = dv_dy[:, :, 1:-1]
        
        # Now all are (B, H-2, W-2)
        
        # Cauchy-Riemann terms
        # The actual map is F(x) = x + phi(x).
        # J_11 = 1 + du_dx
        # J_12 = du_dy
        # J_21 = dv_dx
        # J_22 = 1 + dv_dy
        
        # However, since we are minimizing (J_11 - J_22)^2 + (J_12 + J_21)^2
        # (1 + du_dx - (1 + dv_dy))^2 + (du_dy + dv_dx)^2
        # = (du_dx - dv_dy)^2 + (du_dy + dv_dx)^2
        
        term1 = (du_dx - dv_dy) ** 2
        term2 = (du_dy + dv_dx) ** 2
        
        loss = torch.mean(term1 + term2)
        
        return self.weight * loss

class SmoothnessLoss(nn.Module):
    def __init__(self, weight=0.1):
        super(SmoothnessLoss, self).__init__()
        self.weight = weight
        
    def forward(self, flow):
        # L2 norm of gradients of the flow
        du_dx = (flow[:, :, :, 1:] - flow[:, :, :, :-1]) ** 2
        du_dy = (flow[:, :, 1:, :] - flow[:, :, :-1, :]) ** 2
        
        loss = torch.mean(du_dx) + torch.mean(du_dy)
        return self.weight * loss

"""
Standard CNN baseline models (ResNet, EfficientNet, Vision Transformer).
"""
import torch
import torch.nn as nn
import torchvision.models as models
import timm


class ResNet18Baseline(nn.Module):
    """ResNet-18 baseline model."""
    
    def __init__(self, num_classes: int = 9, pretrained: bool = True):
        super(ResNet18Baseline, self).__init__()
        self.model = models.resnet18(pretrained=pretrained)
        num_ftrs = self.model.fc.in_features
        self.model.fc = nn.Linear(num_ftrs, num_classes)
    
    def forward(self, x):
        return self.model(x)


class ResNet50Baseline(nn.Module):
    """ResNet-50 baseline model."""
    
    def __init__(self, num_classes: int = 9, pretrained: bool = True):
        super(ResNet50Baseline, self).__init__()
        self.model = models.resnet50(pretrained=pretrained)
        num_ftrs = self.model.fc.in_features
        self.model.fc = nn.Linear(num_ftrs, num_classes)
    
    def forward(self, x):
        return self.model(x)


class EfficientNetB0Baseline(nn.Module):
    """EfficientNet-B0 baseline model."""
    
    def __init__(self, num_classes: int = 9, pretrained: bool = True):
        super(EfficientNetB0Baseline, self).__init__()
        if pretrained:
            self.model = timm.create_model('efficientnet_b0', pretrained=True, num_classes=num_classes)
        else:
            self.model = timm.create_model('efficientnet_b0', pretrained=False, num_classes=num_classes)
    
    def forward(self, x):
        return self.model(x)


class VisionTransformerBaseline(nn.Module):
    """Vision Transformer (ViT-B/16) baseline model."""
    
    def __init__(self, num_classes: int = 9, pretrained: bool = True, image_size: int = 224):
        super(VisionTransformerBaseline, self).__init__()
        if pretrained:
            self.model = timm.create_model('vit_base_patch16_224', pretrained=True, num_classes=num_classes)
        else:
            self.model = timm.create_model('vit_base_patch16_224', pretrained=False, num_classes=num_classes)
    
    def forward(self, x):
        return self.model(x)


def get_baseline_model(model_name: str, num_classes: int = 9, pretrained: bool = True, **kwargs):
    """
    Factory function to get baseline model by name.
    
    Args:
        model_name: Name of the model
        num_classes: Number of output classes
        pretrained: Whether to use pretrained weights
        **kwargs: Additional model-specific arguments
        
    Returns:
        Model instance
    """
    models_dict = {
        'resnet18': ResNet18Baseline,
        'resnet50': ResNet50Baseline,
        'efficientnet_b0': EfficientNetB0Baseline,
        'vit': VisionTransformerBaseline,
    }
    
    if model_name not in models_dict:
        raise ValueError(f"Unknown model: {model_name}. Available models: {list(models_dict.keys())}")
    
    model_class = models_dict[model_name]
    return model_class(num_classes=num_classes, pretrained=pretrained, **kwargs)

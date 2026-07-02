"""
Model registry and factory for all implemented models.
"""
import torch.nn as nn
from typing import Optional, Dict, Any

from .dca_model import DCANet
from .baseline_models import (
    ResNet18Baseline,
    ResNet50Baseline,
    EfficientNetB0Baseline,
    VisionTransformerBaseline
)
from .stn_models import STNAffine, STNTPS
from .foundation_models import get_foundation_model
from .simclr import SimCLRModel, SimCLRFineTuneModel
from .stain_normalization import wrap_model_with_stain_normalization


# Model registry
MODEL_REGISTRY = {
    # DCA model
    'dca': DCANet,
    
    # Standard CNN baselines
    'resnet18': ResNet18Baseline,
    'resnet50': ResNet50Baseline,
    'efficientnet_b0': EfficientNetB0Baseline,
    'vit': VisionTransformerBaseline,
    
    # STN variants
    'stn_affine': STNAffine,
    'stn_tps': STNTPS,
    
    # Foundation models (handled separately)
    'plip_linear': lambda **kwargs: get_foundation_model('plip', mode='linear_probe', **kwargs),
    'plip_finetune': lambda **kwargs: get_foundation_model('plip', mode='finetune', **kwargs),
    'uni_linear': lambda **kwargs: get_foundation_model('uni', mode='linear_probe', **kwargs),
    'uni_finetune': lambda **kwargs: get_foundation_model('uni', mode='finetune', **kwargs),
    'conch_linear': lambda **kwargs: get_foundation_model('conch', mode='linear_probe', **kwargs),
    'conch_finetune': lambda **kwargs: get_foundation_model('conch', mode='finetune', **kwargs),
    
    # Self-supervised
    'simclr': SimCLRModel,
    'simclr_finetune': SimCLRFineTuneModel,
}


def get_model(
    model_name: str,
    num_classes: int = 9,
    pretrained: bool = True,
    stain_normalization: bool = False,
    **kwargs
) -> nn.Module:
    """
    Get model by name from registry.
    
    Args:
        model_name: Name of the model
        num_classes: Number of output classes
        pretrained: Whether to use pretrained weights (where applicable)
        stain_normalization: Whether to wrap model with stain normalization
        **kwargs: Additional model-specific arguments
        
    Returns:
        Model instance
    """
    if model_name not in MODEL_REGISTRY:
        available_models = ', '.join(MODEL_REGISTRY.keys())
        raise ValueError(
            f"Unknown model: {model_name}. "
            f"Available models: {available_models}"
        )
    
    model_class = MODEL_REGISTRY[model_name]
    
    # Handle different model initialization signatures
    if model_name == 'dca':
        model = model_class(num_classes=num_classes, backbone=kwargs.get('backbone', 'resnet18'))
    elif model_name in ['stn_affine', 'stn_tps']:
        model = model_class(num_classes=num_classes, backbone=kwargs.get('backbone', 'resnet18'))
    elif model_name in ['simclr']:
        model = model_class(backbone=kwargs.get('backbone', 'resnet18'))
    elif model_name == 'simclr_finetune':
        # For fine-tuning, need pretrained SimCLR model
        raise ValueError("Use SimCLRFineTuneModel.from_pretrained_simclr() instead")
    elif 'linear' in model_name or 'finetune' in model_name:
        # Foundation models
        model = model_class(num_classes=num_classes)
    else:
        # Standard models
        model = model_class(num_classes=num_classes, pretrained=pretrained)
    
    # Wrap with stain normalization if requested
    if stain_normalization:
        model = wrap_model_with_stain_normalization(model)
    
    return model


def list_available_models() -> Dict[str, str]:
    """
    List all available models with descriptions.
    
    Returns:
        Dictionary mapping model names to descriptions
    """
    descriptions = {
        'dca': 'Deep Conformal Alignment (Ours)',
        'resnet18': 'ResNet-18 baseline',
        'resnet50': 'ResNet-50 baseline',
        'efficientnet_b0': 'EfficientNet-B0 baseline',
        'vit': 'Vision Transformer (ViT-B/16)',
        'stn_affine': 'Spatial Transformer Network with Affine transformation',
        'stn_tps': 'Spatial Transformer Network with Thin Plate Spline',
        'plip_linear': 'PLIP foundation model (linear probe)',
        'plip_finetune': 'PLIP foundation model (fine-tuned)',
        'uni_linear': 'UNI foundation model (linear probe)',
        'uni_finetune': 'UNI foundation model (fine-tuned)',
        'conch_linear': 'CONCH foundation model (linear probe)',
        'conch_finetune': 'CONCH foundation model (fine-tuned)',
        'simclr': 'SimCLR self-supervised pretraining',
        'simclr_finetune': 'SimCLR supervised fine-tuning',
    }
    
    return descriptions


def count_parameters(model: nn.Module) -> Dict[str, int]:
    """
    Count model parameters.
    
    Args:
        model: PyTorch model
        
    Returns:
        Dictionary with total, trainable, and non-trainable parameter counts
    """
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    non_trainable_params = total_params - trainable_params
    
    return {
        'total': total_params,
        'trainable': trainable_params,
        'non_trainable': non_trainable_params
    }


__all__ = [
    'get_model',
    'list_available_models',
    'count_parameters',
    'MODEL_REGISTRY',
    'DCANet',
    'ResNet18Baseline',
    'ResNet50Baseline',
    'EfficientNetB0Baseline',
    'VisionTransformerBaseline',
    'STNAffine',
    'STNTPS',
    'SimCLRModel',
    'SimCLRFineTuneModel',
]

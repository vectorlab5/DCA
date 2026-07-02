"""
Configuration management for DCA experiments.
"""
import os
import yaml
from typing import Dict, Any
from omegaconf import OmegaConf


class Config:
    """Configuration manager using OmegaConf."""
    
    def __init__(self, config_path: str = None, overrides: Dict[str, Any] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Path to YAML configuration file
            overrides: Dictionary of configuration overrides
        """
        # Load default config
        default_config_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'configs', 'default.yaml'
        )
        self.cfg = OmegaConf.load(default_config_path)
        
        # Load custom config if provided
        if config_path and os.path.exists(config_path):
            custom_cfg = OmegaConf.load(config_path)
            self.cfg = OmegaConf.merge(self.cfg, custom_cfg)
        
        # Apply overrides
        if overrides:
            override_cfg = OmegaConf.create(overrides)
            self.cfg = OmegaConf.merge(self.cfg, override_cfg)
    
    def get(self, key: str, default=None):
        """Get configuration value by key (supports dot notation)."""
        try:
            return OmegaConf.select(self.cfg, key, default=default)
        except:
            return default
    
    def set(self, key: str, value: Any):
        """Set configuration value by key (supports dot notation)."""
        OmegaConf.update(self.cfg, key, value)
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary."""
        return OmegaConf.to_container(self.cfg, resolve=True)
    
    def save(self, path: str):
        """Save configuration to YAML file."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            OmegaConf.save(self.cfg, f)
    
    def __repr__(self):
        return OmegaConf.to_yaml(self.cfg)


def load_config(config_path: str = None, **kwargs) -> Config:
    """
    Load configuration from file with optional keyword argument overrides.
    
    Args:
        config_path: Path to configuration file
        **kwargs: Configuration overrides
        
    Returns:
        Config object
    """
    return Config(config_path=config_path, overrides=kwargs)

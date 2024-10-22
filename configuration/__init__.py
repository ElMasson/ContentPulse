# configuration/__init__.py

# S'assurer que tous les modules sont importés correctement
from .branding import branding_config
from .personas import personas_config
from .build_matrix import build_matrix_config
from .content_types import content_types_config
from .business_objectives import business_objectives_config

__all__ = [
    'branding_config',
    'personas_config',
    'build_matrix_config',
    'content_types_config',
    'business_objectives_config'
]
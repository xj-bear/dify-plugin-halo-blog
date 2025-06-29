"""
Halo plugin tools.
"""

import importlib.util
import os

# Dynamic import for modules with hyphens in filename
def _import_tool(module_name, class_name):
    """Dynamically import a tool class from a module with hyphen in name."""
    try:
        current_dir = os.path.dirname(__file__)
        module_path = os.path.join(current_dir, f"{module_name}.py")
        spec = importlib.util.spec_from_file_location(module_name.replace('-', '_'), module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return getattr(module, class_name)
    except Exception as e:
        print(f"Error importing {class_name} from {module_name}: {e}")
        return None

# Import all tool classes
HaloSetupTool = _import_tool('halo-setup', 'HaloSetupTool')
HaloPostCreateTool = _import_tool('halo-post-create', 'HaloPostCreateTool')
HaloPostGetTool = _import_tool('halo-post-get', 'HaloPostGetTool')
HaloPostUpdateTool = _import_tool('halo-post-update', 'HaloPostUpdateTool')
HaloPostDeleteTool = _import_tool('halo-post-delete', 'HaloPostDeleteTool')
HaloPostListTool = _import_tool('halo-post-list', 'HaloPostListTool')
HaloMomentCreateTool = _import_tool('halo-moment-create', 'HaloMomentCreateTool')
HaloMomentListTool = _import_tool('halo-moment-list', 'HaloMomentListTool')
HaloCategoriesListTool = _import_tool('halo-categories-list', 'HaloCategoriesListTool')
HaloTagsListTool = _import_tool('halo-tags-list', 'HaloTagsListTool')

# Export tool classes
__all__ = [
    'HaloSetupTool',
    'HaloPostCreateTool',
    'HaloPostGetTool',
    'HaloPostUpdateTool',
    'HaloPostDeleteTool',
    'HaloPostListTool',
    'HaloMomentCreateTool',
    'HaloMomentListTool',
    'HaloCategoriesListTool',
    'HaloTagsListTool'
] 
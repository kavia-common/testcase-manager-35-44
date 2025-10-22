# PUBLIC_INTERFACE
def __package_info__():
    """
    This function exists to mark `src` as a Python package and provide minimal package metadata.
    It allows Python to resolve imports like `from src.core.settings import get_settings`.
    """
    return {
        "name": "robot_backend_src",
        "description": "Root package for the Robot Framework Test Manager backend.",
    }

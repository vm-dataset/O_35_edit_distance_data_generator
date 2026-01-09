"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           YOUR TASK CONFIGURATION                             ║
║                                                                               ║
║  CUSTOMIZE THIS FILE to define your task-specific settings.                   ║
║  Inherits common settings from core.GenerationConfig                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from pydantic import Field
from core import GenerationConfig


class TaskConfig(GenerationConfig):
    """
    Edit Distance Task configuration.
    
    Configuration for generating string transformation tasks where models
    must apply minimum edit operations (insert, delete, replace) to transform
    one string into another.
    
    Inherited from GenerationConfig:
        - num_samples: int          # Number of samples to generate
        - domain: str               # Task domain name (default: "edit_distance")
        - difficulty: Optional[str] # Difficulty level
        - random_seed: Optional[int] # For reproducibility
        - output_dir: Path          # Where to save outputs
        - image_size: tuple[int, int] # Image dimensions
    """
    
    # ══════════════════════════════════════════════════════════════════════════
    #  OVERRIDE DEFAULTS
    # ══════════════════════════════════════════════════════════════════════════
    
    domain: str = Field(default="edit_distance")
    image_size: tuple[int, int] = Field(default=(512, 512))
    
    # ══════════════════════════════════════════════════════════════════════════
    #  VIDEO SETTINGS
    # ══════════════════════════════════════════════════════════════════════════
    
    generate_videos: bool = Field(
        default=True,
        description="Whether to generate ground truth videos"
    )
    
    video_fps: int = Field(
        default=10,
        description="Video frame rate"
    )
    
    video_hold_frames: int = Field(
        default=1,
        description="Frames to hold at start and end of video"
    )
    
    video_operation_frames: int = Field(
        default=6,
        description="Frames per edit operation in video"
    )
    
    # ══════════════════════════════════════════════════════════════════════════
    #  EDIT DISTANCE TASK SETTINGS
    # ══════════════════════════════════════════════════════════════════════════
    
    min_string_length: int = Field(
        default=3,
        description="Minimum length of initial string"
    )
    
    max_string_length: int = Field(
        default=10,
        description="Maximum length of initial string"
    )
    
    min_edit_distance: int = Field(
        default=1,
        description="Minimum edit distance (number of operations)"
    )
    
    max_edit_distance: int = Field(
        default=5,
        description="Maximum edit distance (number of operations)"
    )
    
    use_uppercase: bool = Field(
        default=True,
        description="Use uppercase letters only"
    )
    
    use_lowercase: bool = Field(
        default=False,
        description="Use lowercase letters only"
    )
    
    use_numbers: bool = Field(
        default=False,
        description="Include numbers in strings"
    )
    
    use_mixed_case: bool = Field(
        default=False,
        description="Allow mixed case (overrides use_uppercase/use_lowercase)"
    )
    
    font_size: int = Field(
        default=48,
        description="Font size for text rendering"
    )
    
    text_color: tuple[int, int, int] = Field(
        default=(0, 0, 0),
        description="Text color (RGB)"
    )
    
    background_color: tuple[int, int, int] = Field(
        default=(255, 255, 255),
        description="Background color (RGB)"
    )

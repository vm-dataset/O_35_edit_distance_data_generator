"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    EDIT DISTANCE TASK GENERATOR                              ║
║                                                                               ║
║  Generates tasks where the model must transform one string to another        ║
║  using minimum edit operations (insert, delete, replace).                   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import tempfile
import string
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from PIL import Image, ImageDraw, ImageFont

from core import BaseGenerator, TaskPair, ImageRenderer
from core.video_utils import VideoGenerator
from .config import TaskConfig
from .prompts import get_prompt


class TaskGenerator(BaseGenerator):
    """
    Edit Distance Task Generator.
    
    Generates string transformation tasks where the model must apply
    minimum edit operations to transform initial string to target string.
    """
    
    def __init__(self, config: TaskConfig):
        super().__init__(config)
        self.renderer = ImageRenderer(image_size=config.image_size)
        
        # Initialize video generator if enabled
        self.video_generator = None
        if config.generate_videos and VideoGenerator.is_available():
            self.video_generator = VideoGenerator(fps=config.video_fps, output_format="mp4")
        
        # Initialize font
        self.font = self._get_font(config.font_size)
        
        # Character set based on config
        self.char_set = self._build_char_set()
    
    def generate_task_pair(self, task_id: str) -> TaskPair:
        """Generate one edit distance task pair."""
        
        # Generate string pair with edit operations
        task_data = self._generate_string_pair()
        
        # Render images
        first_image = self._render_text_image(task_data["initial_string"])
        final_image = self._render_text_image(task_data["target_string"])
        
        # Generate video (optional)
        video_path = None
        if self.config.generate_videos and self.video_generator:
            video_path = self._generate_video(
                task_data["initial_string"],
                task_data["target_string"],
                task_data["edit_operations"],
                task_id
            )
        
        # Select prompt based on operation types
        prompt_type = self._determine_prompt_type(task_data["edit_operations"])
        prompt = get_prompt(prompt_type)
        
        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=prompt,
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=video_path
        )
    
    # ══════════════════════════════════════════════════════════════════════════
    #  STRING GENERATION
    # ══════════════════════════════════════════════════════════════════════════
    
    def _build_char_set(self) -> str:
        """Build character set based on configuration."""
        chars = ""
        if self.config.use_uppercase:
            chars += string.ascii_uppercase
        if self.config.use_lowercase:
            chars += string.ascii_lowercase
        if self.config.use_numbers:
            chars += string.digits
        
        if self.config.use_mixed_case:
            chars = string.ascii_letters
            if self.config.use_numbers:
                chars += string.digits
        
        if not chars:
            # Default to uppercase if nothing specified
            chars = string.ascii_uppercase
        
        return chars
    
    def _generate_string_pair(self) -> Dict:
        """
        Generate initial and target strings with minimum edit distance.
        
        Uses Levenshtein distance algorithm to ensure the edit operations
        are the minimum possible.
        """
        # Generate initial string
        initial_length = random.randint(
            self.config.min_string_length,
            self.config.max_string_length
        )
        initial_string = ''.join(random.choices(self.char_set, k=initial_length))
        
        # Generate target string with desired edit distance
        # Try multiple times to get a target string with edit distance in range
        max_attempts = 50
        for attempt in range(max_attempts):
            # Generate target string
            target_length = random.randint(
                max(1, initial_length - self.config.max_edit_distance),
                initial_length + self.config.max_edit_distance
            )
            target_string = ''.join(random.choices(self.char_set, k=target_length))
            
            # Calculate minimum edit distance
            edit_distance, edit_operations = self._compute_min_edit_distance(
                initial_string,
                target_string
            )
            
            # Check if edit distance is in desired range
            if (self.config.min_edit_distance <= edit_distance <= 
                self.config.max_edit_distance):
                return {
                    "initial_string": initial_string,
                    "target_string": target_string,
                    "edit_operations": edit_operations,
                    "edit_distance": edit_distance,
                    "type": self._determine_prompt_type(edit_operations)
                }
        
        # Fallback: if we can't find a good pair, use the last attempt
        edit_distance, edit_operations = self._compute_min_edit_distance(
            initial_string,
            target_string
        )
        return {
            "initial_string": initial_string,
            "target_string": target_string,
            "edit_operations": edit_operations,
            "edit_distance": edit_distance,
            "type": self._determine_prompt_type(edit_operations)
        }
    
    def _compute_min_edit_distance(
        self,
        source: str,
        target: str
    ) -> Tuple[int, List[Dict]]:
        """
        Compute minimum edit distance (Levenshtein distance) and optimal edit sequence.
        
        Uses dynamic programming to find the minimum number of operations
        needed to transform source into target.
        
        Returns:
            (edit_distance, list of edit operations in optimal order)
        """
        m, n = len(source), len(target)
        
        # DP table: dp[i][j] = minimum edit distance from source[0:i] to target[0:j]
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Initialize base cases
        for i in range(m + 1):
            dp[i][0] = i  # Delete all characters from source
        for j in range(n + 1):
            dp[0][j] = j  # Insert all characters into empty source
        
        # Fill DP table
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if source[i - 1] == target[j - 1]:
                    # Characters match, no operation needed
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    # Choose minimum of: replace, delete, or insert
                    dp[i][j] = min(
                        dp[i - 1][j - 1] + 1,  # Replace
                        dp[i - 1][j] + 1,      # Delete
                        dp[i][j - 1] + 1       # Insert
                    )
        
        edit_distance = dp[m][n]
        
        # Backtrack to find optimal edit sequence
        edit_operations = []
        i, j = m, n
        
        while i > 0 or j > 0:
            if i > 0 and j > 0 and source[i - 1] == target[j - 1]:
                # Characters match, move diagonally (no operation)
                i -= 1
                j -= 1
            elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
                # Replace operation
                edit_operations.insert(0, {
                    "type": "replace",
                    "position": i - 1,
                    "old_character": source[i - 1],
                    "new_character": target[j - 1]
                })
                i -= 1
                j -= 1
            elif i > 0 and dp[i][j] == dp[i - 1][j] + 1:
                # Delete operation
                edit_operations.insert(0, {
                    "type": "delete",
                    "position": i - 1,
                    "character": source[i - 1]
                })
                i -= 1
            elif j > 0 and dp[i][j] == dp[i][j - 1] + 1:
                # Insert operation
                edit_operations.insert(0, {
                    "type": "insert",
                    "position": i,
                    "character": target[j - 1]
                })
                j -= 1
        
        return edit_distance, edit_operations
    
    def _determine_prompt_type(self, edit_operations: List[Dict]) -> str:
        """Determine prompt type based on edit operations."""
        if not edit_operations:
            return "default"
        
        op_types = [op["type"] for op in edit_operations]
        has_insert = "insert" in op_types
        has_delete = "delete" in op_types
        has_replace = "replace" in op_types
        
        if has_insert and not has_delete and not has_replace:
            return "insertion"
        elif has_delete and not has_insert and not has_replace:
            return "deletion"
        elif has_replace and not has_insert and not has_delete:
            return "replacement"
        else:
            return "mixed"
    
    # ══════════════════════════════════════════════════════════════════════════
    #  IMAGE RENDERING
    # ══════════════════════════════════════════════════════════════════════════
    
    def _render_text_image(self, text: str) -> Image.Image:
        """Render text string as an image."""
        img = Image.new(
            'RGB',
            self.config.image_size,
            self.config.background_color
        )
        draw = ImageDraw.Draw(img)
        
        # Calculate text position (centered)
        bbox = draw.textbbox((0, 0), text, font=self.font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (self.config.image_size[0] - text_width) // 2
        y = (self.config.image_size[1] - text_height) // 2
        
        # Draw text
        draw.text(
            (x, y),
            text,
            font=self.font,
            fill=self.config.text_color
        )
        
        return img
    
    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Get font for text rendering."""
        # Try to find a monospace font (better for character alignment)
        font_names = [
            "Courier New",
            "Courier",
            "/System/Library/Fonts/Monaco.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
            "DejaVu Sans Mono",
        ]
        
        for font_name in font_names:
            try:
                return ImageFont.truetype(font_name, size)
            except (OSError, IOError):
                continue
        
        # Fallback to default font
        try:
            return ImageFont.truetype("arial.ttf", size)
        except (OSError, IOError):
            return ImageFont.load_default()
    
    # ══════════════════════════════════════════════════════════════════════════
    #  VIDEO GENERATION
    # ══════════════════════════════════════════════════════════════════════════
    
    def _generate_video(
        self,
        initial_string: str,
        target_string: str,
        edit_operations: List[Dict],
        task_id: str
    ) -> Optional[str]:
        """Generate ground truth video showing edit operations."""
        temp_dir = Path(tempfile.gettempdir()) / f"{self.config.domain}_videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        video_path = temp_dir / f"{task_id}_ground_truth.mp4"
        
        # Create animation frames
        frames = self._create_edit_animation_frames(
            initial_string,
            target_string,
            edit_operations
        )
        
        if not frames:
            return None
        
        result = self.video_generator.create_video_from_frames(
            frames,
            video_path
        )
        
        return str(result) if result else None
    
    def _create_edit_animation_frames(
        self,
        initial_string: str,
        target_string: str,
        edit_operations: List[Dict],
        hold_frames: int = 5,
        operation_frames: int = 15
    ) -> List[Image.Image]:
        """
        Create animation frames showing edit operations step by step.
        
        Args:
            initial_string: Starting string
            target_string: Target string
            edit_operations: List of edit operations to apply
            hold_frames: Frames to hold at start and end
            operation_frames: Frames per operation
            
        Returns:
            List of PIL Images representing animation frames
        """
        frames = []
        current_string = list(initial_string)
        
        # Hold initial state
        initial_image = self._render_text_image(initial_string)
        for _ in range(hold_frames):
            frames.append(initial_image)
        
        # Apply each edit operation with animation
        # Note: positions in edit_operations are relative to the original string
        # We need to track the current position mapping as we apply operations
        position_offset = 0  # Track how deletions have shifted positions
        
        for op_idx, operation in enumerate(edit_operations):
            op_type = operation["type"]
            original_pos = operation["position"]
            current_pos = original_pos + position_offset
            
            if op_type == "insert":
                # Animate character insertion
                frames.extend(self._animate_insert(
                    current_string,
                    current_pos,
                    operation["character"],
                    operation_frames
                ))
                current_string.insert(current_pos, operation["character"])
                # Insertions shift positions after this point
                position_offset += 1
            
            elif op_type == "delete":
                # Animate character deletion
                frames.extend(self._animate_delete(
                    current_string,
                    current_pos,
                    operation_frames
                ))
                current_string.pop(current_pos)
                # Deletions shift positions after this point
                position_offset -= 1
            
            elif op_type == "replace":
                # Animate character replacement
                frames.extend(self._animate_replace(
                    current_string,
                    current_pos,
                    operation["old_character"],
                    operation["new_character"],
                    operation_frames
                ))
                current_string[current_pos] = operation["new_character"]
                # Replacements don't change position offset
        
        # Hold final state
        final_image = self._render_text_image(target_string)
        for _ in range(hold_frames):
            frames.append(final_image)
        
        return frames
    
    def _animate_insert(
        self,
        current_string: List[str],
        position: int,
        new_char: str,
        frames: int
    ) -> List[Image.Image]:
        """Animate character insertion (fade in)."""
        animation_frames = []
        
        # Create string with new character inserted (for final state)
        final_string_list = current_string.copy()
        final_string_list.insert(position, new_char)
        final_string = ''.join(final_string_list)
        
        # Create transition frames (fade in)
        for i in range(frames):
            # Interpolate opacity from 0 to 1
            alpha = i / (frames - 1) if frames > 1 else 1.0
            
            # Render base string (without new character)
            display_string = ''.join(current_string)
            base_image = self._render_text_image(display_string)
            
            # Create overlay with new character at position
            overlay = Image.new('RGBA', self.config.image_size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            # Calculate position for new character
            prefix = ''.join(current_string[:position])
            bbox_prefix = draw.textbbox((0, 0), prefix, font=self.font)
            prefix_width = bbox_prefix[2] - bbox_prefix[0] if prefix else 0
            
            # Center text vertically
            img_width, img_height = self.config.image_size
            text_bbox = draw.textbbox((0, 0), display_string, font=self.font)
            text_height = text_bbox[3] - text_bbox[1]
            y = (img_height - text_height) // 2
            
            # Calculate x position
            bbox_all = draw.textbbox((0, 0), display_string, font=self.font)
            text_width = bbox_all[2] - bbox_all[0]
            x_start = (img_width - text_width) // 2
            x = x_start + prefix_width
            
            # Draw character with alpha
            color_with_alpha = (*self.config.text_color, int(255 * alpha))
            draw.text((x, y), new_char, font=self.font, fill=color_with_alpha)
            
            # Composite overlay onto base
            result = Image.alpha_composite(
                base_image.convert('RGBA'),
                overlay
            ).convert('RGB')
            
            animation_frames.append(result)
        
        # Add final stable frame showing the complete result
        final_image = self._render_text_image(final_string)
        animation_frames.append(final_image)
        
        return animation_frames
    
    def _animate_delete(
        self,
        current_string: List[str],
        position: int,
        frames: int
    ) -> List[Image.Image]:
        """Animate character deletion (fade out)."""
        animation_frames = []
        char_to_delete = current_string[position]
        
        # Create final string (without deleted character)
        final_string_list = current_string.copy()
        final_string_list.pop(position)
        final_string = ''.join(final_string_list)
        
        for i in range(frames):
            # Interpolate opacity from 1 to 0
            alpha = 1.0 - (i / (frames - 1) if frames > 1 else 1.0)
            
            # Render base string (final state without the character)
            base_image = self._render_text_image(final_string)
            
            # Create overlay with fading character
            overlay = Image.new('RGBA', self.config.image_size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            # Calculate position for character to delete
            prefix = ''.join(current_string[:position])
            bbox_prefix = draw.textbbox((0, 0), prefix, font=self.font)
            prefix_width = bbox_prefix[2] - bbox_prefix[0] if prefix else 0
            
            # Center text vertically
            img_width, img_height = self.config.image_size
            text_bbox = draw.textbbox((0, 0), final_string, font=self.font)
            text_height = text_bbox[3] - text_bbox[1]
            y = (img_height - text_height) // 2
            
            # Calculate x position
            bbox_all = draw.textbbox((0, 0), final_string, font=self.font)
            text_width = bbox_all[2] - bbox_all[0]
            x_start = (img_width - text_width) // 2
            x = x_start + prefix_width
            
            # Draw character with decreasing alpha (fade out)
            color_with_alpha = (*self.config.text_color, int(255 * alpha))
            draw.text((x, y), char_to_delete, font=self.font, fill=color_with_alpha)
            
            # Composite overlay onto base
            result = Image.alpha_composite(
                base_image.convert('RGBA'),
                overlay
            ).convert('RGB')
            
            animation_frames.append(result)
        
        # Add final stable frame showing the complete result (without deleted char)
        final_image = self._render_text_image(final_string)
        animation_frames.append(final_image)
        
        return animation_frames
    
    def _animate_replace(
        self,
        current_string: List[str],
        position: int,
        old_char: str,
        new_char: str,
        frames: int
    ) -> List[Image.Image]:
        """Animate character replacement (fade out old, fade in new)."""
        animation_frames = []
        
        # Create final string (with replaced character)
        final_string_list = current_string.copy()
        final_string_list[position] = new_char
        final_string = ''.join(final_string_list)
        
        for i in range(frames):
            # Interpolate: old char fades out, new char fades in
            progress = i / (frames - 1) if frames > 1 else 1.0
            old_alpha = 1.0 - progress
            new_alpha = progress
            
            # Render base string (final state with new character)
            base_image = self._render_text_image(final_string)
            
            # Create overlay
            overlay = Image.new('RGBA', self.config.image_size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            # Calculate position
            prefix = ''.join(current_string[:position])
            bbox_prefix = draw.textbbox((0, 0), prefix, font=self.font)
            prefix_width = bbox_prefix[2] - bbox_prefix[0] if prefix else 0
            
            # Center text vertically
            img_width, img_height = self.config.image_size
            text_bbox = draw.textbbox((0, 0), final_string, font=self.font)
            text_height = text_bbox[3] - text_bbox[1]
            y = (img_height - text_height) // 2
            
            # Calculate x position
            bbox_all = draw.textbbox((0, 0), final_string, font=self.font)
            text_width = bbox_all[2] - bbox_all[0]
            x_start = (img_width - text_width) // 2
            x = x_start + prefix_width
            
            # Draw old character (fading out) - overlay on top
            if old_alpha > 0:
                color_old = (*self.config.text_color, int(255 * old_alpha))
                draw.text((x, y), old_char, font=self.font, fill=color_old)
            
            # Note: new_char is already in base_image, so we don't need to draw it again
            # The fade-in effect comes from old_char fading out
            
            # Composite
            result = Image.alpha_composite(
                base_image.convert('RGBA'),
                overlay
            ).convert('RGB')
            
            animation_frames.append(result)
        
        # Add final stable frame showing the complete result (with new character)
        final_image = self._render_text_image(final_string)
        animation_frames.append(final_image)
        
        return animation_frames

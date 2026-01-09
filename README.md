# Edit Distance Task Data Generator 🎲

Generates string transformation tasks where models must apply minimum edit operations (insert, delete, replace) to transform one string into another. Compatible with VMEvalKit framework.

This task generator follows the [template-data-generator](https://github.com/vm-dataset/template-data-generator.git) format and is compatible with [VMEvalKit](https://github.com/Video-Reason/VMEvalKit.git).

Repository: [O_35_edit_distance_data_generator](https://github.com/vm-dataset/O_35_edit_distance_data_generator)

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/vm-dataset/O_35_edit_distance_data_generator.git
cd O_35_edit_distance_data_generator

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# 4. Generate tasks
python examples/generate.py --num-samples 50
```

---

## 📁 Structure

```
edit-distance-task-data-generator/
├── core/                    # ✅ Standard utilities
│   ├── base_generator.py   # Abstract base class
│   ├── schemas.py         # Pydantic models
│   ├── image_utils.py      # Image helpers
│   ├── video_utils.py      # Video generation
│   └── output_writer.py    # File output
├── src/                     # Edit distance task implementation
│   ├── generator.py        # Edit distance task generator
│   ├── prompts.py          # Task prompt templates
│   └── config.py           # Task configuration
├── examples/
│   └── generate.py         # Entry point
└── data/questions/         # Generated output
```

---

## 📦 Output Format

Every generator produces:

```
data/questions/{domain}_task/{task_id}/
├── first_frame.png          # Initial state (REQUIRED)
├── final_frame.png          # Goal state (or goal.txt)
├── prompt.txt               # Instructions (REQUIRED)
└── ground_truth.mp4         # Solution video (OPTIONAL)
```

---

## 🎨 Customization (3 Files to Modify)

### 1. Update `src/generator.py`

The edit distance task generator is already implemented:

```python
from core import BaseGenerator, TaskPair, ImageRenderer

class TaskGenerator(BaseGenerator):
    def __init__(self, config):
        super().__init__(config)
        self.renderer = ImageRenderer(config.image_size)
    
    def generate_task_pair(self, task_id: str) -> TaskPair:
        # 1. Generate string pair with edit operations
        task_data = self._generate_string_pair()
        
        # 2. Render images
        first_image = self._render_text_image(task_data["initial_string"])
        final_image = self._render_text_image(task_data["target_string"])
        
        # 3. Generate video (optional)
        video_path = self._generate_video(...)
        
        # 4. Create TaskPair
        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=get_prompt(task_data.get("type", "default")),
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=video_path
        )
```

### 2. Update `src/prompts.py`

Edit distance task prompts are already defined:

```python
PROMPTS = {
    "default": [
        "Transform the text by applying the minimum number of edit operations...",
        "Edit the initial text to become the target text using the fewest operations...",
    ],
    "insertion": [...],
    "deletion": [...],
    "replacement": [...],
    "mixed": [...],
}

def get_prompt(task_type: str = "default") -> str:
    prompts = PROMPTS.get(task_type, PROMPTS["default"])
    return random.choice(prompts)
```

### 3. Update `src/config.py`

**All hyperparameters are configured** - both general and task-specific:

```python
from core import GenerationConfig
from pydantic import Field

class TaskConfig(GenerationConfig):
    """Edit distance task-specific configuration."""
    # Inherits: num_samples, domain, seed, output_dir, image_size
    
    # Override defaults
    domain: str = Field(default="edit_distance")
    image_size: tuple[int, int] = Field(default=(512, 512))
    
    # Task-specific hyperparameters
    min_string_length: int = Field(default=3, description="Minimum string length")
    max_string_length: int = Field(default=10, description="Maximum string length")
    min_edit_distance: int = Field(default=1, description="Minimum edit distance")
    max_edit_distance: int = Field(default=5, description="Maximum edit distance")
    use_uppercase: bool = Field(default=True, description="Use uppercase letters")
    font_size: int = Field(default=48, description="Font size for text rendering")
```

**Single entry point:** `python examples/generate.py --num-samples 50`
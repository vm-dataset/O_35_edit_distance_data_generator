"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           YOUR TASK PROMPTS                                   ║
║                                                                               ║
║  CUSTOMIZE THIS FILE to define prompts/instructions for your task.            ║
║  Prompts are selected based on task type and returned to the model.           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random


# ══════════════════════════════════════════════════════════════════════════════
#  DEFINE YOUR PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

PROMPTS = {
    "default": [
        """The scene shows two text strings: an initial string in the first frame and a target string in the final frame. Transform the initial string into the target string using the minimum number of edit operations. You can use three operations: (1) Insert a character at a position, (2) Delete a character from a position, or (3) Replace a character at a position. Execute operations sequentially from left to right, one at a time. Each operation must be clearly visible: show new characters appearing for inserts, characters disappearing for deletes, and characters changing for replaces. After all operations, the transformed string must exactly match the target string in both length and content. Verify every character matches its corresponding position in the target.""",
        
        """The scene displays an initial text string and a target text string side by side. Apply character-level edit operations to transform the initial string into the target string using the optimal sequence (minimum edit distance). Available operations: insertion (add character), deletion (remove character), and replacement (change character). Work systematically from left to right, applying one operation at a time. Use the minimum number of operations possible. Make each operation visible: insertions show new characters appearing, deletions show characters being removed, replacements show old characters being changed to new ones. The final result must be identical to the target string - same length, same characters, same positions.""",
        
        """The scene contains two text frames: initial string on the left and target string on the right. Transform the initial string to match the target exactly using edit operations. You have three operation types: insert (add character at position), delete (remove character at position), and replace (change character at position). Apply operations sequentially from left to right, one at a time, minimizing total operations. For each operation, clearly show the position, character(s) involved, and result. Continue until the string fully matches the target. Verify every character in the final result corresponds exactly to the target string in both value and position.""",
    ],
    
    "insertion": [
        """The scene shows two text strings: an initial string in the first frame and a longer target string in the final frame. The target contains additional characters missing from the initial string. Insert the missing characters into the initial string at their correct positions to transform it into the target string. Starting from the left, identify each position where a character needs to be inserted. For each insertion, add the missing character at that exact position, shifting all subsequent characters to the right. Perform insertions sequentially from left to right, one character at a time. Each inserted character should appear clearly at its designated position. After all insertions, the resulting string must match the target exactly in both length and content.""",
        
        """The scene displays an initial string and a longer target string. The target has more characters, so characters must be inserted. Transform the initial string into the target by adding missing characters at their correct positions. Work from left to right. At each position where a character is missing, insert the required character from the target string. After each insertion, the string length increases by one, and all characters to the right shift one position. Continue until all missing characters are inserted and the string matches the target completely. The final result must be identical to the target string in every character and position.""",
    ],
    
    "deletion": [
        """The scene shows two text strings: an initial string in the first frame and a shorter target string in the final frame. The initial string contains extra characters that must be removed. Delete the unnecessary characters from the initial string, one at a time, until it matches the target exactly. Starting from the left, compare the initial string with the target to identify which characters need deletion. For each character to remove, delete it from its current position, causing all characters to the right to shift one position left. Perform deletions sequentially. After each deletion, re-evaluate the remaining string against the target. Continue until the string length and content exactly match the target. Each deleted character should visibly disappear from the string.""",
        
        """The scene displays an initial string longer than the target string. Some characters must be deleted. Transform the initial string into the target by removing extra characters. Work from left to right. At each position, determine if the current character should remain (matches target) or be deleted (extra). When deleting, remove the character completely, and all characters after it shift left by one position. Perform deletions one at a time, checking after each deletion that the remaining string can still be transformed into the target. Continue until the string matches the target exactly in length and content. The final result must contain only the characters in the target string, in the correct order.""",
    ],
    
    "replacement": [
        """The scene shows two text strings of equal length: an initial string in the first frame and a target string in the final frame. The strings differ only in some character values at specific positions. Replace the incorrect characters in the initial string with the correct characters from the target string. Starting from the leftmost position, compare each character in the initial string with the corresponding character in the target. At each position where characters differ, replace the character in the initial string with the character from the target. Perform replacements sequentially from left to right, one at a time. For each replacement, show the old character being removed and the new character appearing. Continue until all positions match. Verify the transformed string is identical to the target at every position.""",
        
        """The scene displays an initial string and a target string of the same length. These strings differ in character values at certain positions. Transform the initial string into the target by replacing characters that do not match. Work position by position from left to right. At each position, check if the character matches the target. If not, replace it with the corresponding character from the target string. Execute each replacement one at a time, making each change clearly visible. After each replacement, the character at that position should match the target. Continue until every position contains the correct character. The final transformed string must be identical to the target string in all positions.""",
    ],
    
    "mixed": [
        """The scene shows two text strings: an initial string in the first frame and a target string in the final frame. The strings may differ in length and/or character content, requiring a combination of edit operations. Apply the minimum number of edit operations needed using the optimal sequence. You can perform three operation types: insert a character at a position, delete a character from a position, or replace a character at a position. Work systematically from left to right, applying operations in the order that minimizes total operations. For each operation, clearly show: insertions have new characters appearing, deletions have characters being removed, replacements have old characters changing to new. Continue until the string exactly matches the target in both length and content. Verify the final result is identical to the target in every character and position.""",
        
        """The scene displays an initial text string and a target text string that differ in content and/or length, requiring multiple types of edit operations. Transform the initial string into the target using a combination of insert, delete, and replace operations, ensuring minimum total operations. Starting from the leftmost position, compare the strings and determine needed operations: insert missing characters, delete extra characters, and/or replace incorrect characters. Apply operations sequentially, one at a time, choosing the most efficient sequence. Make each operation clearly visible: show insertions as new characters appearing, deletions as characters disappearing, replacements as characters changing. After all operations, the transformed string must match the target exactly - same length, same characters, same positions. Verify every character in the final result corresponds to the target.""",
        
        """The scene contains two text frames: initial string on the left and target string on the right, requiring mixed edit operations. Apply the minimum edit distance to convert the initial string into the target. You have three operation types: INSERT (add character, shift right), DELETE (remove character, shift left), and REPLACE (substitute character, length unchanged). Plan the optimal sequence that minimizes total operations, then execute sequentially from left to right, one operation at a time. Show each operation clearly: inserted characters appear, deleted characters disappear, replaced characters change. After each operation, update the string state and continue. The final string must be identical to the target: same length, each character matches its corresponding position. Ensure no character is missed or incorrectly processed.""",
    ],
}


def get_prompt(task_type: str = "default") -> str:
    """
    Select a random prompt for the given task type.
    
    Args:
        task_type: Type of task (key in PROMPTS dict)
        
    Returns:
        Random prompt string from the specified type
    """
    prompts = PROMPTS.get(task_type, PROMPTS["default"])
    return random.choice(prompts)


def get_all_prompts(task_type: str = "default") -> list[str]:
    """Get all prompts for a given task type."""
    return PROMPTS.get(task_type, PROMPTS["default"])

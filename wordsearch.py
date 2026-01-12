"""
Word Search Puzzle Generator (Backtracking)

- Places words into a grid using backtracking.
- Allows words in 8 directions (horizontal, vertical, diagonal).
- Fills remaining empty cells with random letters.

Run:
    python wordsearch.py
"""

from __future__ import annotations
import random
import string
from typing import List, Tuple, Optional

EMPTY = "·"  # Visible placeholder while debugging 


Direction = Tuple[int, int]
Placement = Tuple[int, int, Direction]  # row, col, direction


DIRECTIONS_8: List[Direction] = [
    (0, 1),   # right
    (0, -1),  # left
    (1, 0),   # down
    (-1, 0),  # up
    (1, 1),   # down-right
    (1, -1),  # down-left
    (-1, 1),  # up-right
    (-1, -1), # up-left
]


def make_empty_grid(size: int) -> List[List[str]]:
    """Create a size x size grid filled with EMPTY placeholders."""
    return [[EMPTY for _ in range(size)] for _ in range(size)]


def in_bounds(size: int, r: int, c: int) -> bool:
    """Check if (r, c) is inside a size x size grid."""
    return 0 <= r < size and 0 <= c < size


def can_place_word(grid: List[List[str]], word: str, r: int, c: int, dr: int, dc: int) -> bool:
    """
    Return True if 'word' can be placed starting at (r, c) moving by (dr, dc),
    without going out of bounds and without conflicting with existing letters.
    """
    size = len(grid)
    for i, ch in enumerate(word):
        rr = r + i * dr
        cc = c + i * dc
        if not in_bounds(size, rr, cc):
            return False
        cell = grid[rr][cc]
        if cell != EMPTY and cell != ch:
            return False
    return True


def place_word(grid: List[List[str]], word: str, r: int, c: int, dr: int, dc: int) -> List[Tuple[int, int]]:
    """
    Place 'word' into the grid. Returns a list of coordinates that were changed
    from EMPTY to a letter (so we can undo cleanly during backtracking).
    """
    changed: List[Tuple[int, int]] = []
    for i, ch in enumerate(word):
        rr = r + i * dr
        cc = c + i * dc
        if grid[rr][cc] == EMPTY:
            grid[rr][cc] = ch
            changed.append((rr, cc))
    return changed


def undo_changes(grid: List[List[str]], changed: List[Tuple[int, int]]) -> None:
    """Undo a placement by resetting only the cells that were originally EMPTY."""
    for r, c in changed:
        grid[r][c] = EMPTY


def all_possible_placements(grid: List[List[str]], word: str, directions: List[Direction]) -> List[Placement]:
    """
    Generate all (row, col, direction) placements where the word *could* fit.
    We shuffle later to randomize puzzles.
    """
    size = len(grid)
    placements: List[Placement] = []
    for r in range(size):
        for c in range(size):
            for dr, dc in directions:
                if dr == 0 and dc == 0:
                    continue
                if can_place_word(grid, word, r, c, dr, dc):
                    placements.append((r, c, (dr, dc)))
    return placements


def backtrack_place_words(
    grid: List[List[str]],
    words: List[str],
    idx: int,
    directions: List[Direction],
    rng: random.Random
) -> bool:
    """
    Backtracking:
    - Try to place words[idx] in a valid spot.
    - Recurse for the next word.
    - If later words fail, undo and try a different placement.
    """
    if idx == len(words):
        return True  # All words placed

    word = words[idx]
    placements = all_possible_placements(grid, word, directions)
    rng.shuffle(placements)  # randomize the look of the puzzle

    for r, c, (dr, dc) in placements:
        changed = place_word(grid, word, r, c, dr, dc)
        if backtrack_place_words(grid, words, idx + 1, directions, rng):
            return True
        undo_changes(grid, changed)

    return False  # No placement worked for this word


def fill_empty_with_random_letters(grid: List[List[str]], rng: random.Random) -> None:
    """Replace EMPTY cells with random uppercase letters."""
    for r in range(len(grid)):
        for c in range(len(grid)):
            if grid[r][c] == EMPTY:
                grid[r][c] = rng.choice(string.ascii_uppercase)


def print_grid(grid: List[List[str]]) -> None:
    """Pretty-print the grid."""
    for row in grid:
        print(" ".join(row))


def generate_wordsearch(
    words: List[str],
    size: int = 12,
    allow_diagonals: bool = True,
    seed: Optional[int] = None,
) -> List[List[str]]:
    """
    Generate a word search grid.

    - words are uppercased and sorted by length (longer first is easier for backtracking).
    - returns the final grid with random letters filled in.
    """
    rng = random.Random(seed)

    cleaned = [w.strip().upper().replace(" ", "") for w in words if w.strip()]
    cleaned.sort(key=len, reverse=True)

    grid = make_empty_grid(size)

    directions = DIRECTIONS_8 if allow_diagonals else [(0, 1), (0, -1), (1, 0), (-1, 0)]

    success = backtrack_place_words(grid, cleaned, 0, directions, rng)
    if not success:
        raise ValueError(
            "Could not place all words. Try a bigger grid, fewer words, or disable diagonals."
        )

    fill_empty_with_random_letters(grid, rng)
    return grid


if __name__ == "__main__":
    # Example usage:
    WORDS = [
        "PYTHON",
        "BACKTRACKING",
        "ALGORITHM",
        "GRID",
        "PUZZLE",
        "FUNCTION",
        "DEBUG",
    ]

    grid = generate_wordsearch(WORDS, size=12, allow_diagonals=True, seed=42)
    print("\nWORD SEARCH:\n")
    print_grid(grid)
    print("\nWORDS:")
    print(", ".join([w.upper() for w in WORDS]))

"""Game logic utilities for the number guessing game."""
import json
import os
from datetime import datetime, UTC
from typing import Dict, List, Optional


DEFAULT_HIGH_SCORES_FILE = "high_scores.json"


def get_range_for_difficulty(difficulty: str) -> tuple[int, int]:
    """
    Get the inclusive number range for a given difficulty level.

    Difficulty levels determine the range of possible secret numbers
    and affect the scoring system. Each difficulty has a unique range
    that balances challenge and playability.

    Args:
        difficulty: The difficulty level as a string.
                   Valid values: "Easy", "Normal", "Hard"

    Returns:
        tuple[int, int]: A tuple of (low, high) representing the inclusive
                        range boundaries for the secret number.
                        - Easy: (1, 20)
                        - Normal: (1, 50)
                        - Hard: (1, 100)
                        - Default: (1, 50) for unrecognized difficulty

    Examples:
        >>> get_range_for_difficulty("Easy")
        (1, 20)
        >>> get_range_for_difficulty("Hard")
        (1, 100)
    """
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        # FIXME: Was 1, 100. Changed to 1, 50 for proper
        # difficulty progression.
        return 1, 50
    if difficulty == "Hard":
        # FIXME: Was 1, 50 which made Hard easier than Normal.
        # Changed to 1, 100.
        return 1, 100
    return 1, 50


def parse_guess(raw: str) -> tuple[bool, int | None, str | None]:
    """
    Parse and validate user input into an integer guess.

    Accepts numeric strings (including decimals) and converts them to integers.
    Decimal values are truncated (not rounded) to integers. Empty strings,
    None values, and non-numeric input are rejected with appropriate error messages.

    Args:
        raw: The raw user input string to parse. Can be a number, decimal,
             empty string, or non-numeric text.

    Returns:
        tuple[bool, int | None, str | None]: A 3-tuple containing:
            - ok (bool): True if parsing succeeded, False otherwise
            - guess_int (int | None): The parsed integer value, or None if parsing failed
            - error_message (str | None): Error message if parsing failed, or None if successful

    Examples:
        >>> parse_guess("42")
        (True, 42, None)
        >>> parse_guess("2.9")
        (True, 2, None)  # Truncated, not rounded
        >>> parse_guess("")
        (False, None, "Enter a guess.")
        >>> parse_guess("abc")
        (False, None, "That is not a number.")

    Note:
        Decimal values are truncated using int(float(x)), so 2.9 becomes 2, not 3.
        Negative numbers and values outside the valid range are accepted by the
        parser but should be validated separately by the game logic.
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw == "":
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess: int | str, secret: int | str) -> tuple[str, str]:
    """
    Compare a player's guess to the secret number and return the outcome.

    Determines whether the guess is correct, too high, or too low compared to
    the secret number. Handles both integer and string comparisons for type
    flexibility (useful for testing edge cases). Returns both a classification
    and a user-friendly message with emoji indicators.

    Args:
        guess: The player's guessed number (int or str for type flexibility)
        secret: The secret number to guess (int or str for type flexibility)

    Returns:
        tuple[str, str]: A 2-tuple containing:
            - outcome (str): Classification of the guess. One of:
                * "Win" - Guess matches the secret
                * "Too High" - Guess is greater than the secret
                * "Too Low" - Guess is less than the secret
            - message (str): User-friendly feedback message with emoji:
                * "🎉 Correct!" - For wins
                * "📉 Go LOWER!" - When guess is too high
                * "📈 Go HIGHER!" - When guess is too low

    Examples:
        >>> check_guess(50, 50)
        ('Win', '🎉 Correct!')
        >>> check_guess(60, 50)
        ('Too High', '📉 Go LOWER!')
        >>> check_guess(40, 50)
        ('Too Low', '📈 Go HIGHER!')

    Note:
        The function handles TypeError exceptions to support mixed-type comparisons
        (e.g., comparing int to str), which can occur during certain game states
        or when testing edge cases.
    """
    if guess == secret:
        return "Win", "🎉 Correct!"

    try:
        if guess > secret:
            # FIXME: Was "Go HIGHER!" but should be "Go LOWER!"
            # when guess is too high
            return "Too High", "📉 Go LOWER!"
        else:
            # FIXME: Was "Go LOWER!" but should be "Go HIGHER!"
            # when guess is too low
            return "Too Low", "📈 Go HIGHER!"
    except TypeError:
        g = str(guess)
        if g == secret:
            return "Win", "🎉 Correct!"
        if g > secret:
            # FIXME: Was "Go HIGHER!" but should be "Go LOWER!"
            # when guess is too high
            return "Too High", "📉 Go LOWER!"
        # FIXME: Was "Go LOWER!" but should be "Go HIGHER!"
        # when guess is too low
        return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int) -> int:
    """
    Calculate and return the updated score based on guess outcome.

    The scoring system rewards quick wins and penalizes excessive guessing.
    Winning on earlier attempts yields more points. Incorrect guesses have
    varying point adjustments to add strategic depth to the game.

    Scoring Rules:
        - Win: 100 - 10 × (attempt_number + 1), with a minimum of 10 points
          * 1st attempt (attempt_number=0): 90 points
          * 2nd attempt (attempt_number=1): 80 points
          * 3rd attempt (attempt_number=2): 70 points
          * etc., minimum 10 points for very late wins

        - Too High:
          * Even attempt numbers (0, 2, 4...): +5 points
          * Odd attempt numbers (1, 3, 5...): -5 points

        - Too Low: -5 points (always)

        - Other outcomes: No change to score

    Args:
        current_score: The player's score before this guess
        outcome: The result of the guess comparison. Expected values:
                "Win", "Too High", "Too Low"
        attempt_number: Zero-indexed attempt count (0 = first attempt,
                       1 = second attempt, etc.)

    Returns:
        int: The updated score after applying the outcome's point adjustment

    Examples:
        >>> update_score(0, "Win", 0)  # Win on first attempt
        90
        >>> update_score(0, "Win", 2)  # Win on third attempt
        70
        >>> update_score(50, "Too High", 0)  # Even attempt
        55
        >>> update_score(50, "Too High", 1)  # Odd attempt
        45
        >>> update_score(50, "Too Low", 0)
        45

    Note:
        The alternating point adjustment for "Too High" guesses creates
        strategic variation where the penalty/reward depends on when the
        guess is made in the sequence.
    """
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score


# High Score Tracking Functions


def load_high_scores(
    filepath: str = DEFAULT_HIGH_SCORES_FILE
) -> Dict[str, List[dict]]:
    """
    Load high scores from a JSON file with robust error handling.

    Reads and validates the high scores data structure from disk. If the file
    doesn't exist (first run) or is corrupted, returns an empty but valid
    structure. This ensures the game never crashes due to high score data issues.

    Args:
        filepath: Path to the high scores JSON file, relative to this module.
                 Defaults to "high_scores.json" in the same directory.

    Returns:
        Dict[str, List[dict]]: High scores organized by difficulty level.
            Structure:
            {
                "Easy": [
                    {
                        "score": int,
                        "attempts": int,
                        "timestamp": str (ISO 8601 format),
                        "player_name": str
                    },
                    ...
                ],
                "Normal": [...],
                "Hard": [...]
            }
            Each difficulty list is sorted by score (descending), then by
            attempts (ascending) for tiebreaking.

    Examples:
        >>> scores = load_high_scores()
        >>> scores["Easy"]
        [{'score': 80, 'attempts': 2, 'timestamp': '2026-03-14T10:00:00', 'player_name': 'Alice'}]

    Error Handling:
        - FileNotFoundError: Returns empty structure (first run scenario)
        - JSONDecodeError: Returns empty structure, logs warning
        - Invalid structure: Returns empty structure with validated keys
        - Permission errors: Returns empty structure, logs warning

    Note:
        This function is designed to never raise exceptions. All errors are
        caught and logged, with safe defaults returned to keep the game running.
    """
    default_structure = {
        "Easy": [],
        "Normal": [],
        "Hard": []
    }

    # Get full path relative to this file
    full_path = os.path.join(os.path.dirname(__file__), filepath)

    try:
        with open(full_path, 'r') as f:
            loaded = json.load(f)

        # Validate structure
        if not isinstance(loaded, dict):
            return default_structure

        # Ensure all difficulties exist
        for difficulty in ["Easy", "Normal", "Hard"]:
            if (difficulty not in loaded or
                    not isinstance(loaded[difficulty], list)):
                loaded[difficulty] = []

        return loaded

    except FileNotFoundError:
        # First run, no file yet
        return default_structure

    except json.JSONDecodeError:
        # Corrupted file
        print(f"Warning: {filepath} is corrupted. Using empty scores.")
        return default_structure

    except Exception as e:
        # Catch-all for unexpected errors
        print(f"Warning: Error loading high scores: {e}")
        return default_structure


def save_high_scores(
    high_scores: Dict[str, List[dict]],
    filepath: str = DEFAULT_HIGH_SCORES_FILE
) -> bool:
    """
    Save high scores to a JSON file with pretty formatting.

    Writes the high scores dictionary to disk in a human-readable JSON format
    with indentation and sorted keys. If the save operation fails for any reason
    (permissions, disk space, etc.), the function logs a warning but does not
    raise an exception, allowing the game to continue.

    Args:
        high_scores: Dictionary containing high scores organized by difficulty.
                    Must have the structure:
                    {"Easy": [...], "Normal": [...], "Hard": [...]}
        filepath: Path to save file, relative to this module.
                 Defaults to "high_scores.json" in the same directory.

    Returns:
        bool: True if save operation succeeded, False if any error occurred.
             The game can continue even if False is returned; the player
             just won't receive credit for their high score.

    Examples:
        >>> scores = {"Easy": [{"score": 80, "attempts": 2, ...}], "Normal": [], "Hard": []}
        >>> save_high_scores(scores)
        True

    Error Handling:
        - PermissionError: Returns False, logs warning (file not writable)
        - IOError/OSError: Returns False, logs warning (disk full, network drive issues)
        - Other exceptions: Returns False, logs warning (unexpected errors)

    Note:
        The JSON is formatted with indent=2 and sort_keys=True for readability,
        making it easy to inspect or manually edit the high scores file if needed.
        All errors are caught to prevent the game from crashing.
    """
    # Get full path relative to this file
    full_path = os.path.join(os.path.dirname(__file__), filepath)

    try:
        # Write with pretty printing for readability
        with open(full_path, 'w') as f:
            json.dump(high_scores, f, indent=2, sort_keys=True)
        return True

    except (PermissionError, IOError, OSError) as e:
        print(f"Warning: Could not save high scores: {e}")
        return False

    except Exception as e:
        print(f"Warning: Unexpected error saving high scores: {e}")
        return False


def is_high_score(
    score: int,
    difficulty: str,
    high_scores: Dict[str, List[dict]],
    max_entries: int = 5
) -> bool:
    """
    Determine if a score qualifies for the high score leaderboard.

    A score qualifies if either:
    1. The leaderboard has fewer than max_entries scores (not yet full), OR
    2. The score is better than the worst score currently on the leaderboard

    This allows players to earn a spot on the leaderboard even if other
    players have already achieved high scores, as long as there's room or
    their score is competitive.

    Args:
        score: The score to evaluate for qualification
        difficulty: The difficulty level to check against.
                   Must be "Easy", "Normal", or "Hard"
        high_scores: Current high scores dictionary containing all difficulty
                    leaderboards. Structure matches load_high_scores() return.
        max_entries: Maximum number of scores to keep per difficulty leaderboard.
                    Defaults to 5. If the list is full, only scores better than
                    the worst entry will qualify.

    Returns:
        bool: True if the score qualifies for the leaderboard (either because
             there's space or it beats the worst score), False otherwise.

    Examples:
        >>> scores = {"Easy": [], "Normal": [], "Hard": []}
        >>> is_high_score(50, "Easy", scores)  # Empty list, always qualifies
        True

        >>> scores = {"Easy": [{"score": 80, ...}, {"score": 70, ...}, {"score": 60, ...}], ...}
        >>> is_high_score(65, "Easy", scores, max_entries=5)  # List not full
        True

        >>> scores = {"Easy": [{"score": 80, ...}, ..., {"score": 40, ...}], ...}  # 5 entries
        >>> is_high_score(45, "Easy", scores, max_entries=5)  # Beats worst (40)
        True
        >>> is_high_score(35, "Easy", scores, max_entries=5)  # Worse than worst
        False

    Note:
        This function only checks qualification; it doesn't modify the leaderboard.
        Use add_high_score() to actually add a qualifying score to the leaderboard.
    """
    scores_list = high_scores.get(difficulty, [])

    # If list not full, any score qualifies
    if len(scores_list) < max_entries:
        return True

    # If list is full, check if better than worst score
    if scores_list:
        worst_score = min(entry['score'] for entry in scores_list)
        return score > worst_score

    return True  # Empty list, any score qualifies


def add_high_score(
    score: int,
    attempts: int,
    difficulty: str,
    high_scores: Dict[str, List[dict]],
    player_name: str = "Anonymous",
    max_entries: int = 5
) -> Dict[str, List[dict]]:
    """
    Add a new high score to the leaderboard and return the updated dictionary.

    Creates a new high score entry with the current timestamp, adds it to the
    appropriate difficulty leaderboard, sorts all entries, and trims the list
    to keep only the top scores. The original high_scores dictionary is modified
    in place and also returned.

    Sorting Behavior:
        Scores are sorted by two criteria (in order):
        1. Score (descending): Higher scores rank first
        2. Attempts (ascending): For tied scores, fewer attempts rank first

    Args:
        score: The score achieved by the player
        attempts: Number of attempts the player used to win.
                 Used for tiebreaking when scores are equal.
        difficulty: The difficulty level for this score.
                   Must be "Easy", "Normal", or "Hard"
        high_scores: Current high scores dictionary. Will be modified in place
                    to include the new score.
        player_name: Name of the player to credit. Defaults to "Anonymous".
                    Can be customized for future multiplayer features.
        max_entries: Maximum number of scores to keep per difficulty leaderboard.
                    Defaults to 5. After adding and sorting, the list is trimmed
                    to this size, removing the lowest-ranking entries.

    Returns:
        Dict[str, List[dict]]: The updated high scores dictionary with the new
                              score added, sorted, and trimmed. This is the same
                              object passed in (modified in place), but returned
                              for convenience in chaining operations.

    Examples:
        >>> scores = {"Easy": [], "Normal": [], "Hard": []}
        >>> updated = add_high_score(80, 2, "Easy", scores)
        >>> len(updated["Easy"])
        1
        >>> updated["Easy"][0]["score"]
        80

        >>> scores = {"Easy": [{"score": 90, "attempts": 1, ...}], ...}
        >>> updated = add_high_score(85, 2, "Easy", scores)
        >>> updated["Easy"][0]["score"]  # 90 still first
        90
        >>> updated["Easy"][1]["score"]  # 85 now second
        85

    Note:
        - The timestamp is automatically generated in UTC ISO 8601 format
        - Tiebreaking by attempts rewards efficiency (fewer guesses = higher rank)
        - The list is always trimmed to max_entries, so adding a score when the
          list is full will remove the lowest-ranking entry
        - This function should only be called after is_high_score() confirms
          the score qualifies, though it will work regardless
    """
    # Create new entry
    new_entry = {
        "score": score,
        "attempts": attempts,
        "timestamp": datetime.now(UTC).isoformat(),
        "player_name": player_name
    }

    # Get current scores for this difficulty
    scores_list = high_scores.get(difficulty, [])

    # Add new score
    scores_list.append(new_entry)

    # Sort by score descending, then by attempts ascending (tiebreaker)
    scores_list.sort(key=lambda x: (-x['score'], x['attempts']))

    # Keep only top max_entries
    scores_list = scores_list[:max_entries]

    # Update dictionary
    high_scores[difficulty] = scores_list

    return high_scores


def get_rank(
    score: int,
    difficulty: str,
    high_scores: Dict[str, List[dict]]
) -> Optional[int]:
    """
    Calculate the leaderboard rank for a given score.

    Determines what position (1-indexed) a score would occupy on the leaderboard
    for a specific difficulty. This is used to display achievement messages like
    "You ranked #3!" when a player achieves a high score.

    The rank is calculated by counting how many existing scores are better than
    the given score. Since the leaderboard is already sorted (by add_high_score),
    the function can stop early once it finds a score equal to or worse than
    the given score.

    Args:
        score: The score to calculate rank for
        difficulty: The difficulty level to rank within.
                   Must be "Easy", "Normal", or "Hard"
        high_scores: Current high scores dictionary containing the sorted
                    leaderboards for all difficulty levels.

    Returns:
        Optional[int]: The 1-indexed rank position (1 = first place, 2 = second, etc.),
                      or None if the score wouldn't qualify for the leaderboard.
                      Rank 1 means the score is the best on the leaderboard.

    Examples:
        >>> scores = {"Easy": [], "Normal": [], "Hard": []}
        >>> get_rank(50, "Easy", scores)  # First score on empty leaderboard
        1

        >>> scores = {"Easy": [{"score": 90, ...}, {"score": 80, ...}], ...}
        >>> get_rank(95, "Easy", scores)  # Better than all existing
        1
        >>> get_rank(85, "Easy", scores)  # Between 90 and 80
        2
        >>> get_rank(75, "Easy", scores)  # Worse than all existing
        3

    Note:
        - This function should be called BEFORE adding the score to get the correct rank
        - The rank represents where the score will be positioned after insertion
        - Ranks are calculated independently for each difficulty level
        - The function assumes the leaderboard is already sorted (maintained by add_high_score)
    """
    scores_list = high_scores.get(difficulty, [])

    # Count how many scores are better
    rank = 1
    for entry in scores_list:
        if entry['score'] > score:
            rank += 1
        else:
            break  # List is sorted, no need to continue

    # Return the rank (will be the position where this score would be inserted)
    return rank

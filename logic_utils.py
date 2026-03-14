def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        # FIXME: Was 1, 100. Changed to 1, 50 for proper difficulty progression.
        return 1, 50
    if difficulty == "Hard":
        # FIXME: Was 1, 50 which made Hard easier than Normal. Changed to 1, 100.
        return 1, 100
    return 1, 50


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
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


def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    if guess == secret:
        return "Win", "🎉 Correct!"

    try:
        if guess > secret:
            # FIXME: Was "Go HIGHER!" but should be "Go LOWER!" when guess is too high
            return "Too High", "📉 Go LOWER!"
        else:
            # FIXME: Was "Go LOWER!" but should be "Go HIGHER!" when guess is too low
            return "Too Low", "📈 Go HIGHER!"
    except TypeError:
        g = str(guess)
        if g == secret:
            return "Win", "🎉 Correct!"
        if g > secret:
            # FIXME: Was "Go HIGHER!" but should be "Go LOWER!" when guess is too high
            return "Too High", "📉 Go LOWER!"
        # FIXME: Was "Go LOWER!" but should be "Go HIGHER!" when guess is too low
        return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
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

from logic_utils import check_guess, get_range_for_difficulty


# Bug 1 Fix: Inverted hints - When guess > secret, should say "Go LOWER!"
def test_too_high():
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"
    assert "LOWER" in message


# Bug 1 Fix: Inverted hints - When guess < secret, should say "Go HIGHER!"
def test_too_low():
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message


# Bug 1 Fix: Correct guess returns Win
def test_win():
    outcome, message = check_guess(50, 50)
    assert outcome == "Win"
    assert "Correct" in message


# Bug 2 Fix: Hard mode should be harder than Normal (bigger range)
def test_hard_range():
    _, normal_high = get_range_for_difficulty("Normal")
    _, hard_high = get_range_for_difficulty("Hard")
    assert hard_high > normal_high  # Hard was 50, should be 500

from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    parse_guess,
    load_high_scores,
    save_high_scores,
    is_high_score,
    add_high_score,
    get_rank
)


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


# ========== EDGE CASE TESTS ==========

# Edge Case 1: Negative numbers should be parsed but are outside valid range
def test_negative_number_parsing():
    ok, value, err = parse_guess("-5")
    assert ok is True  # Parser accepts it
    assert value == -5  # Value is negative
    assert err is None


def test_negative_number_always_too_low():
    # On Easy mode (1-20), -5 should always be too low
    outcome, message = check_guess(-5, 10)
    assert outcome == "Too Low"
    assert "HIGHER" in message


# Edge Case 2: Out-of-range large numbers
def test_large_number_parsing():
    ok, value, err = parse_guess("999999")
    assert ok is True  # Parser accepts it
    assert value == 999999
    assert err is None


def test_large_number_always_too_high():
    # On Hard mode (max 100), 999999 should always be too high
    outcome, message = check_guess(999999, 50)
    assert outcome == "Too High"
    assert "LOWER" in message


# Edge Case 3: Decimal truncation
def test_decimal_truncation():
    ok, value, err = parse_guess("2.9")
    assert ok is True
    assert value == 2  # Should truncate to 2, not round to 3
    assert err is None


def test_decimal_truncation_affects_comparison():
    # If user enters 2.9 but it becomes 2, and secret is 3
    ok, value, err = parse_guess("2.9")
    outcome, message = check_guess(value, 3)
    # User thinks they guessed 2.9 or 3, but actually guessed 2
    assert value == 2
    assert outcome == "Too Low"  # 2 < 3


def test_high_decimal_truncation():
    ok, value, err = parse_guess("49.99")
    assert ok is True
    assert value == 49  # Truncates down, not up to 50
    assert err is None


# Boundary tests: Valid range limits
def test_exact_boundary_low():
    # Test that 1 is accepted (lower boundary for all difficulties)
    ok, value, err = parse_guess("1")
    assert ok is True
    assert value == 1


def test_exact_boundary_high():
    # Test that 100 is accepted (upper boundary for Hard mode)
    ok, value, err = parse_guess("100")
    assert ok is True
    assert value == 100


# Invalid input tests
def test_empty_string():
    ok, value, err = parse_guess("")
    assert ok is False
    assert value is None
    assert err == "Enter a guess."


def test_non_numeric_string():
    ok, value, err = parse_guess("abc")
    assert ok is False
    assert value is None
    assert err == "That is not a number."


# ========== HIGH SCORE TESTS ==========

def test_load_high_scores_file_not_exists(tmp_path):
    """Test that loading non-existent file returns empty structure."""
    test_file = tmp_path / "nonexistent.json"
    result = load_high_scores(str(test_file))
    assert result == {"Easy": [], "Normal": [], "Hard": []}


def test_save_and_load_roundtrip(tmp_path):
    """Test that saving and loading preserves data."""
    test_file = tmp_path / "scores.json"
    test_data = {
        "Easy": [{"score": 80, "attempts": 2, "timestamp":
                  "2026-03-14T10:00:00", "player_name": "Test"}],
        "Normal": [],
        "Hard": []
    }
    success = save_high_scores(test_data, str(test_file))
    assert success is True
    loaded = load_high_scores(str(test_file))
    assert loaded == test_data


def test_is_high_score_empty_list():
    """Test that first score always qualifies."""
    high_scores = {"Easy": [], "Normal": [], "Hard": []}
    result = is_high_score(50, "Easy", high_scores)
    assert result is True


def test_is_high_score_better_than_worst():
    """Test that score qualifies if it beats the lowest score."""
    high_scores = {
        "Easy": [
            {"score": 80, "attempts": 2, "timestamp":
             "2026-03-14T10:00:00", "player_name": "Test"},
            {"score": 70, "attempts": 3, "timestamp":
             "2026-03-14T11:00:00", "player_name": "Test"},
            {"score": 60, "attempts": 4, "timestamp":
             "2026-03-14T12:00:00", "player_name": "Test"},
            {"score": 50, "attempts": 5, "timestamp":
             "2026-03-14T13:00:00", "player_name": "Test"},
            {"score": 40, "attempts": 6, "timestamp":
             "2026-03-14T14:00:00", "player_name": "Test"}
        ],
        "Normal": [],
        "Hard": []
    }
    result = is_high_score(45, "Easy", high_scores, max_entries=5)
    assert result is True


def test_is_high_score_worse_than_worst():
    """Test that score doesn't qualify if below all existing scores."""
    high_scores = {
        "Easy": [
            {"score": 80, "attempts": 2, "timestamp":
             "2026-03-14T10:00:00", "player_name": "Test"},
            {"score": 70, "attempts": 3, "timestamp":
             "2026-03-14T11:00:00", "player_name": "Test"},
            {"score": 60, "attempts": 4, "timestamp":
             "2026-03-14T12:00:00", "player_name": "Test"},
            {"score": 50, "attempts": 5, "timestamp":
             "2026-03-14T13:00:00", "player_name": "Test"},
            {"score": 40, "attempts": 6, "timestamp":
             "2026-03-14T14:00:00", "player_name": "Test"}
        ],
        "Normal": [],
        "Hard": []
    }
    result = is_high_score(30, "Easy", high_scores, max_entries=5)
    assert result is False


def test_add_high_score_sorts_correctly():
    """Test that new score is inserted in correct position."""
    high_scores = {
        "Easy": [
            {"score": 80, "attempts": 2, "timestamp":
             "2026-03-14T10:00:00", "player_name": "Test"},
            {"score": 60, "attempts": 4, "timestamp":
             "2026-03-14T12:00:00", "player_name": "Test"}
        ],
        "Normal": [],
        "Hard": []
    }
    updated = add_high_score(70, 3, "Easy", high_scores)
    assert updated["Easy"][0]["score"] == 80
    assert updated["Easy"][1]["score"] == 70
    assert updated["Easy"][2]["score"] == 60


def test_add_high_score_trims_to_max():
    """Test that list is limited to max_entries."""
    high_scores = {
        "Easy": [
            {"score": 80, "attempts": 2, "timestamp":
             "2026-03-14T10:00:00", "player_name": "Test"},
            {"score": 70, "attempts": 3, "timestamp":
             "2026-03-14T11:00:00", "player_name": "Test"},
            {"score": 60, "attempts": 4, "timestamp":
             "2026-03-14T12:00:00", "player_name": "Test"},
            {"score": 50, "attempts": 5, "timestamp":
             "2026-03-14T13:00:00", "player_name": "Test"},
            {"score": 40, "attempts": 6, "timestamp":
             "2026-03-14T14:00:00", "player_name": "Test"}
        ],
        "Normal": [],
        "Hard": []
    }
    updated = add_high_score(65, 4, "Easy", high_scores, max_entries=5)
    assert len(updated["Easy"]) == 5
    assert updated["Easy"][-1]["score"] == 50


def test_get_rank_first_place():
    """Test that highest score returns rank 1."""
    high_scores = {
        "Easy": [
            {"score": 80, "attempts": 2, "timestamp":
             "2026-03-14T10:00:00", "player_name": "Test"},
            {"score": 70, "attempts": 3, "timestamp":
             "2026-03-14T11:00:00", "player_name": "Test"}
        ],
        "Normal": [],
        "Hard": []
    }
    rank = get_rank(90, "Easy", high_scores)
    assert rank == 1


def test_get_rank_middle_position():
    """Test that score in middle returns correct rank."""
    high_scores = {
        "Easy": [
            {"score": 80, "attempts": 2, "timestamp":
             "2026-03-14T10:00:00", "player_name": "Test"},
            {"score": 70, "attempts": 3, "timestamp":
             "2026-03-14T11:00:00", "player_name": "Test"},
            {"score": 60, "attempts": 4, "timestamp":
             "2026-03-14T12:00:00", "player_name": "Test"}
        ],
        "Normal": [],
        "Hard": []
    }
    rank = get_rank(75, "Easy", high_scores)
    assert rank == 2


def test_full_high_score_workflow(tmp_path):
    """Test complete workflow: load → check → add → save → load → verify."""
    test_file = tmp_path / "workflow.json"

    # Load (file doesn't exist yet)
    high_scores = load_high_scores(str(test_file))
    assert high_scores["Easy"] == []

    # Check if score qualifies
    qualifies = is_high_score(80, "Easy", high_scores)
    assert qualifies is True

    # Get rank
    rank = get_rank(80, "Easy", high_scores)
    assert rank == 1

    # Add score
    updated = add_high_score(80, 2, "Easy", high_scores)
    assert len(updated["Easy"]) == 1

    # Save
    success = save_high_scores(updated, str(test_file))
    assert success is True

    # Load again and verify persistence
    reloaded = load_high_scores(str(test_file))
    assert len(reloaded["Easy"]) == 1
    assert reloaded["Easy"][0]["score"] == 80

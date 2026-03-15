import random
import streamlit as st
from logic_utils import (
    get_range_for_difficulty,
    parse_guess,
    check_guess,
    update_score,
    load_high_scores,
    save_high_scores,
    is_high_score,
    add_high_score,
    get_rank
)

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

st.sidebar.divider()
st.sidebar.subheader("🏆 High Scores")

# Load and display high scores for current difficulty
high_scores = load_high_scores()
difficulty_scores = high_scores.get(difficulty, [])

if difficulty_scores:
    for i, entry in enumerate(difficulty_scores[:5], 1):
        if i == 1:
            medal = "🥇"
        elif i == 2:
            medal = "🥈"
        elif i == 3:
            medal = "🥉"
        else:
            medal = f"{i}."

        st.sidebar.caption(
            f"{medal} {entry['score']} pts ({entry['attempts']} att.)"
        )
else:
    st.sidebar.caption("No high scores yet! Be the first!")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    st.session_state.attempts = 0  # Start at 0, increments before each guess

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

if "last_hint" not in st.session_state:
    st.session_state.last_hint = None

# Only show game interface if game is still in progress
if st.session_state.status == "playing":
    st.subheader("Make a guess")

    # Progress bar for attempts
    progress_value = st.session_state.attempts / attempt_limit
    st.progress(
        progress_value,
        text=f"Attempts: {st.session_state.attempts}/{attempt_limit}"
    )

    # Big score display
    col_score1, col_score2 = st.columns([1, 3])
    with col_score1:
        st.metric(label="Current Score", value=st.session_state.score)
    with col_score2:
        # FIXME: Was hardcoded "1 and 100". Changed to use {low} and {high} variables.
        st.info(
            f"Guess a number between {low} and {high}. "
            f"Attempts left: {attempt_limit - st.session_state.attempts}"
        )

    # FIXME: Wrapped in st.form() so Enter key submits the guess
    with st.form("guess_form", clear_on_submit=True):
        raw_guess = st.text_input(
            "Enter your guess:",
            key=f"guess_input_{difficulty}"
        )
        submit = st.form_submit_button("Submit Guess 🚀", use_container_width=True)

    # Game controls
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        new_game = st.button("🔁 New Game", use_container_width=True)
    with col2:
        show_hint = st.checkbox("💡 Show hints", value=True)
    with col3:
        pass  # Empty for spacing

    # Display last hint above Recent Guesses
    if show_hint and st.session_state.last_hint:
        hint_type, hint_message = st.session_state.last_hint
        if hint_type == "error":
            st.error(hint_message)
        elif hint_type == "info":
            st.info(hint_message)
        elif hint_type == "success":
            st.success(hint_message)

    # Guess history cards (last 5 guesses) - collapsible
    if st.session_state.history:
        with st.expander("📊 Recent Guesses", expanded=True):
            history_display = st.session_state.history[-5:]  # Last 5 only
            cols = st.columns(min(len(history_display), 5))
            for i, guess in enumerate(history_display):
                with cols[i]:
                    st.metric(label=f"#{len(st.session_state.history) - len(history_display) + i + 1}", value=str(guess))
else:
    # Game is over - show New Game button prominently
    new_game = st.button("🔁 Start New Game", type="primary", use_container_width=True)
    show_hint = True  # Default value when game is over
    submit = False  # No submit when game is over

# FIXME: Reset all game state properly when starting new game
if new_game:
    st.session_state.attempts = 0  # Reset to 0
    # Use difficulty range, not hardcoded 1-100
    st.session_state.secret = random.randint(low, high)
    st.session_state.score = 0  # Reset score
    st.session_state.status = "playing"  # Reset status
    st.session_state.history = []  # Clear history
    st.session_state.last_hint = None  # Clear last hint
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")

    # Post-game summary table
    if st.session_state.history:
        st.subheader("Game Summary")
        summary_data = []
        for i, guess in enumerate(st.session_state.history, 1):
            if isinstance(guess, int):
                diff = guess - st.session_state.secret
                if diff == 0:
                    result = "✅ Correct!"
                elif diff > 0:
                    result = f"🔻 Too High (+{diff})"
                else:
                    result = f"🔺 Too Low ({diff})"
            else:
                result = "❌ Invalid"
            summary_data.append({
                "Attempt": i,
                "Guess": str(guess),
                "Result": result
            })

        # Display as table
        st.table(summary_data)

        # Game statistics
        valid_guesses = [g for g in st.session_state.history if isinstance(g, int)]
        if valid_guesses:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Attempts", len(st.session_state.history))
            with col2:
                st.metric("Valid Guesses", len(valid_guesses))
            with col3:
                st.metric("Final Score", st.session_state.score)

    st.stop()

if submit:
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.session_state.last_hint = ("error", err)
        st.rerun()
    else:
        st.session_state.history.append(guess_int)

        if st.session_state.attempts % 2 == 0:
            secret = str(st.session_state.secret)
        else:
            secret = st.session_state.secret

        outcome, message = check_guess(guess_int, secret)

        # Calculate proximity for hot/cold indicator
        distance = abs(guess_int - st.session_state.secret)
        range_size = high - low
        proximity_pct = (range_size - distance) / range_size * 100

        if proximity_pct >= 90:
            temp_emoji = "🔥🔥🔥"
            temp_text = "BURNING HOT!"
        elif proximity_pct >= 70:
            temp_emoji = "🔥🔥"
            temp_text = "Very Hot"
        elif proximity_pct >= 50:
            temp_emoji = "🔥"
            temp_text = "Hot"
        elif proximity_pct >= 30:
            temp_emoji = "🌡️"
            temp_text = "Warm"
        elif proximity_pct >= 15:
            temp_emoji = "❄️"
            temp_text = "Cold"
        else:
            temp_emoji = "❄️❄️"
            temp_text = "Ice Cold"

        # Store hint in session state for display above Recent Guesses
        if outcome == "Too High":
            st.session_state.last_hint = ("error", f"🔻 {message} | {temp_emoji} {temp_text}")
        elif outcome == "Too Low":
            st.session_state.last_hint = ("info", f"🔺 {message} | {temp_emoji} {temp_text}")
        elif outcome == "Win":
            st.session_state.last_hint = ("success", f"🎯 {message}")

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"

            # Check and save high score
            high_scores = load_high_scores()

            if is_high_score(st.session_state.score, difficulty,
                             high_scores):
                # Calculate rank before adding (to show correct position)
                rank = get_rank(
                    st.session_state.score, difficulty, high_scores
                )

                # Add and save new high score
                updated_scores = add_high_score(
                    score=st.session_state.score,
                    attempts=st.session_state.attempts,
                    difficulty=difficulty,
                    high_scores=high_scores
                )
                save_high_scores(updated_scores)

                # Celebrate new high score
                st.success(
                    f"🎉 NEW HIGH SCORE! You ranked #{rank} "
                    f"on {difficulty} mode!\n\n"
                    f"The secret was {st.session_state.secret}. "
                    f"Final score: {st.session_state.score}"
                )
            else:
                # Regular win message
                st.success(
                    f"You won! The secret was {st.session_state.secret}. "
                    f"Final score: {st.session_state.score}"
                )
            st.rerun()
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )
                st.rerun()
            else:
                # Game continues, rerun to update UI immediately
                st.rerun()

# Full Leaderboard for all difficulties
with st.expander("🏆 Leaderboard - All Difficulties"):
    high_scores = load_high_scores()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**🟢 Easy Mode**")
        easy_scores = high_scores.get("Easy", [])
        if easy_scores:
            for i, entry in enumerate(easy_scores, 1):
                st.write(
                    f"{i}. **{entry['score']}** pts "
                    f"({entry['attempts']} att.)"
                )
        else:
            st.caption("No scores yet")

    with col2:
        st.markdown("**🟡 Normal Mode**")
        normal_scores = high_scores.get("Normal", [])
        if normal_scores:
            for i, entry in enumerate(normal_scores, 1):
                st.write(
                    f"{i}. **{entry['score']}** pts "
                    f"({entry['attempts']} att.)"
                )
        else:
            st.caption("No scores yet")

    with col3:
        st.markdown("**🔴 Hard Mode**")
        hard_scores = high_scores.get("Hard", [])
        if hard_scores:
            for i, entry in enumerate(hard_scores, 1):
                st.write(
                    f"{i}. **{entry['score']}** pts "
                    f"({entry['attempts']} att.)"
                )
        else:
            st.caption("No scores yet")

# FIXME: Moved debug info AFTER submit logic so history updates immediately
with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")

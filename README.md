# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] **Game's Purpose:** This is a number guessing game where you try to guess a secret number. It has three difficulty levels - Easy gives you a smaller range (1-20), Normal is medium (1-50), and Hard is the biggest range (1-100). When you guess, the game tells you if you should go higher or lower. You get a limited number of attempts based on the difficulty, and the faster you win, the better your score.

- [x] **Bugs I Found:** I discovered 6 major bugs:
  1. **Inverted hints** - Told me to go higher when I was already too high
  2. **Backwards difficulty** - Hard mode (1-50) was easier than Normal mode (1-100)
  3. **Wrong range display** - Always showed "1 to 100" regardless of difficulty
  4. **No Enter key** - Had to click the button, couldn't press Enter
  5. **Incomplete reset** - New Game didn't clear score, status, or history
  6. **Delayed history** - Debug info didn't update until next interaction

- [x] **How I Fixed It:**
  1. **Fixed hints** - Swapped comparison logic so "LOWER" shows when too high, "HIGHER" when too low
  2. **Fixed difficulty ranges** - Changed Hard to 1-100 and Normal to 1-50
  3. **Made range dynamic** - Used `{low}` and `{high}` variables instead of hardcoded "1 and 100"
  4. **Added Enter key** - Wrapped input in `st.form()` with `clear_on_submit=True`
  5. **Complete reset** - Made New Game reset all state: attempts, secret, score, status, history
  6. **Immediate updates** - Moved debug info after submit logic
  7. **Code organization** - Refactored all logic functions into `logic_utils.py`

## 📸 Demo

- [ ] [Insert a screenshot of your fixed, winning game here]

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, insert a screenshot of your Enhanced Game UI here]

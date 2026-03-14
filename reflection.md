# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start
  (for example: "the hints were backwards").

**Bug 1: Inverted Hint Messages**
- **Expected:** When my guess is too high, the game should tell me "Go LOWER!" and when my guess is too low, it should tell me "Go HIGHER!"
- **Actually Happened:** The hints were backwards. When `guess > secret`, the message says "📈 Go HIGHER!" (which is wrong - I need to go lower). Similarly, when `guess < secret`, it says "📉 Go LOWER!" (wrong - I need to go higher).

**Bug 2: Hard Mode Has Smaller Range Than Normal Mode**
- **Expected:** Hard difficulty should have a larger number range than Normal mode to make it more challenging (fewer clues in a bigger space).
- **Actually Happened:** Hard mode uses range 1-50, while Normal mode uses range 1-100. This makes "Hard" mode actually easier than "Normal" mode, which is backwards.

**Bug 3: Info Message Shows Wrong Range**
- **Expected:** The info message should display the actual range based on the selected difficulty (e.g., "Guess a number between 1 and 20" for Easy mode).
- **Actually Happened:** The message is hardcoded to always say "Guess a number between 1 and 100" regardless of the difficulty setting. This misleads the player about what range they should be guessing in.

**Bug 4: Pressing Enter Doesn't Submit the Guess**
- **Expected:** When typing a guess in the text input field, pressing Enter should submit the guess automatically, like most web forms work.
- **Actually Happened:** The text input and submit button are separate elements. Pressing Enter in the text field doesn't trigger the submit button - you must manually click "Submit Guess".

**Bug 5: New Game Button Doesn't Reset History**
- **Expected:** When clicking "New Game", all game state should reset including the guess history, so you start completely fresh.
- **Actually Happened:** The new game button only resets attempts and generates a new secret number. It doesn't reset the score, status, or history list, so old guesses from previous games remain visible in the debug info.

**Bug 6: Submitted Guess Doesn't Show in History Immediately**
- **Expected:** After clicking "Submit Guess", the number should immediately appear in the history list shown in the debug info.
- **Actually Happened:** The debug info expander is rendered before the submit button is processed. Even though the guess gets added to the history in session state, you don't see it displayed until the next interaction, making it confusing to track what you've already guessed.

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
  Claude Code
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
  The AI suggested wrapping the text input in `st.form()` with `clear_on_submit=True` to enable Enter key submission, explaining this is Streamlit's only official way to implement this feature. I verified it by testing the app - pressing Enter after typing a guess successfully submitted the form and cleared the input field as expected.

- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).
  The AI initially tried to place all three buttons (Submit Guess, New Game, Show Hint) in the same row inside `st.form()`, mixing `st.form_submit_button()` with regular `st.button()` components. When I ran the app, it crashed with error: `StreamlitAPIException: st.button() can't be used in an st.form()`. This revealed Streamlit's hard constraint that forms can only contain input widgets and form_submit_button, not regular buttons.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
  I played the game myself after each change to see if the bug still happened. For example, after fixing the inverted hints, I intentionally guessed too high and too low to make sure the messages were correct. I also ran pytest to check if the logic functions returned the right values.

- Describe at least one test you ran (manual or using pytest) and what it showed you about your code.
  I ran `test_too_high()` which tests when guess (60) is higher than secret (50). The test checks if the message contains "LOWER". At first this test failed because my code was saying "Go HIGHER!" instead. After I fixed the if statement in `check_guess()`, the test passed.

- Did AI help you design or understand any tests? How?
  AI explained why the test uses `assert "LOWER" in message` instead of checking the whole message exactly. This way the test still works even if I change the emoji or exact wording later, as long as "LOWER" is somewhere in the message.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

  Streamlit is like a movie that replays from the beginning every time you interact with it. Every time you click a button or type something, the entire script runs again from top to bottom. This means normal variables reset to their starting values each time. That's where `st.session_state` comes in - it's like a notebook that remembers things between reruns. So if you want to keep track of the secret number, your score, or your guess history, you store them in session state and they'll stick around even when the script reruns.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?

  I want to keep using pytest to verify my fixes instead of just manually testing. Writing tests like `test_too_high()` helped me catch bugs I might have missed, and they give me confidence that my code actually works. It's also easier to see exactly what's broken when a test fails with a clear assertion error.

- What is one thing you would do differently next time you work with AI on a coding task?

  Next time I'll test AI suggestions before assuming they'll work. When AI suggested putting regular buttons inside a Streamlit form, I should have quickly tested it instead of trusting it completely. Running the code first would have saved time and taught me about Streamlit's constraints faster.

- In one or two sentences, describe how this project changed the way you think about AI generated code.

  AI can write code fast, but it's not always correct - it can make mistakes just like humans. I learned that AI is a helpful teammate for getting started and explaining concepts, but I still need to test everything and understand what the code is actually doing before trusting it.

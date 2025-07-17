import gradio as gr
import random

# ===== Session State ===== #
flashcards = []
current_index = 0
show_answer = False
streak = 0
theme_mode = "light"
quiz_score = 0
quiz_index = 0
quiz_mode_cards = []
shuffle_mode = False

# ===== Available Categories ===== #
categories = [
    "Mathematics", "Science", "Physics", "Physical Education",
    "Information Technology", "Social Studies", "Human and Social Biology",
    "History", "Other"
]

# ===== Functions ===== #

def add_flashcard(question, answer, category):
    flashcards.append({"question": question, "answer": answer, "category": category})
    return f"Added to '{category}'!"

def next_flashcard(selected_category):
    global current_index, show_answer, streak
    filtered = [c for c in flashcards if c['category'] == selected_category] if selected_category else flashcards

    if not filtered:
        return "No flashcards found.", "", f"0 cards", streak

    if shuffle_mode:
        random.shuffle(filtered)

    if current_index >= len(filtered):
        current_index = 0
        streak = 0

    show_answer = False
    card = filtered[current_index]
    return card['question'], "Click 'Flip'", f"{current_index+1}/{len(filtered)} cards", streak

def flip_card(selected_category):
    global show_answer
    filtered = [c for c in flashcards if c['category'] == selected_category] if selected_category else flashcards

    if not filtered:
        return "No flashcards available.", ""

    card = filtered[current_index]
    if show_answer:
        show_answer = False
        return card['question'], "Click 'Flip'"
    else:
        show_answer = True
        return card['question'], card['answer']

def mark_answer(correct, selected_category):
    global current_index, streak
    if correct:
        streak += 1
    else:
        streak = 0

    filtered = [c for c in flashcards if c['category'] == selected_category] if selected_category else flashcards
    current_index += 1
    if current_index >= len(filtered):
        current_index = 0

    return next_flashcard(selected_category)

def toggle_theme(current):
    return "dark" if "light" in current else "light"

def toggle_shuffle():
    global shuffle_mode
    shuffle_mode = not shuffle_mode
    return f"Shuffle: {'On' if shuffle_mode else 'Off'}"

def start_quiz(selected_category):
    global quiz_mode_cards, quiz_score, quiz_index
    quiz_mode_cards = [c for c in flashcards if c['category'] == selected_category] if selected_category else flashcards
    if shuffle_mode:
        random.shuffle(quiz_mode_cards)
    quiz_score = 0
    quiz_index = 0
    if not quiz_mode_cards:
        return "No cards to quiz.", ""
    return quiz_mode_cards[quiz_index]['question'], ""

def submit_quiz_answer(user_answer):
    global quiz_index, quiz_score
    correct_answer = quiz_mode_cards[quiz_index]['answer']
    feedback = ""

    if user_answer.strip().lower() == correct_answer.strip().lower():
        quiz_score += 1
        feedback = "✔️ Correct!"
    else:
        feedback = f"❌ Incorrect! The correct answer was: {correct_answer}"

    quiz_index += 1
    if quiz_index >= len(quiz_mode_cards):
        result = f"Quiz Done! Score: {quiz_score}/{len(quiz_mode_cards)}"
        return result, ""
    else:
        next_q = quiz_mode_cards[quiz_index]['question']
        return f"{feedback}\n\nNext Question: {next_q}", ""

# ===== Interface ===== #

with gr.Blocks(theme="default") as demo:
    gr.Markdown("# 🎴 Spicy Flashcard Trainer 🔥")

    with gr.Tab("➕ Add Flashcard"):
        with gr.Row():
            q_input = gr.Textbox(label="Question")
            a_input = gr.Textbox(label="Answer")
            category_input = gr.Dropdown(choices=categories, value="Other", label="Category")
        add_btn = gr.Button("Add Flashcard")
        add_output = gr.Textbox(label="Status")

    with gr.Tab("🎴 Review Mode"):
        category_filter = gr.Dropdown(choices=[""] + categories, value="", label="Filter Category")
        question_display = gr.Textbox(label="Question")
        answer_display = gr.Textbox(label="Answer/Flip")

        with gr.Row():
            flip_btn = gr.Button("Flip")
            correct_btn = gr.Button("✔️ Correct")
            wrong_btn = gr.Button("❌ Incorrect")

        progress_label = gr.Label()
        streak_label = gr.Label()
        shuffle_btn = gr.Button("Toggle Shuffle")

    with gr.Tab("📝 Quiz Mode"):
        quiz_category = gr.Dropdown(choices=[""] + categories, value="", label="Filter Category")
        quiz_q = gr.Textbox(label="Quiz Question")
        quiz_a = gr.Textbox(label="Your Answer")
        start_quiz_btn = gr.Button("Start Quiz")
        submit_quiz_btn = gr.Button("Submit Answer")

    with gr.Tab("⚙️ Settings"):
        theme_toggle = gr.Button("Switch Theme")
        theme_status = gr.Label(value="Current Theme: light")

    # Add Card
    add_btn.click(fn=add_flashcard, inputs=[q_input, a_input, category_input], outputs=add_output)

    # Review Mode
    category_filter.change(fn=next_flashcard, inputs=category_filter, outputs=[question_display, answer_display, progress_label, streak_label])
    flip_btn.click(fn=flip_card, inputs=category_filter, outputs=[question_display, answer_display])
    correct_btn.click(fn=lambda cat: mark_answer(True, cat), inputs=category_filter, outputs=[question_display, answer_display, progress_label, streak_label])
    wrong_btn.click(fn=lambda cat: mark_answer(False, cat), inputs=category_filter, outputs=[question_display, answer_display, progress_label, streak_label])
    shuffle_btn.click(fn=toggle_shuffle, outputs=shuffle_btn)

    # Quiz Mode
    start_quiz_btn.click(fn=start_quiz, inputs=quiz_category, outputs=[quiz_q, quiz_a])
    submit_quiz_btn.click(fn=submit_quiz_answer, inputs=quiz_a, outputs=[quiz_q, quiz_a])

    # Theme
    theme_toggle.click(fn=toggle_theme, inputs=theme_status, outputs=theme_status)

demo.launch()

import uuid
from flask import Flask, render_template, request, redirect, url_for, session
import sys
import os

def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

# Global cache for questions per quiz session
question_cache = {}

# Function to get random questions for a quiz session
def get_random_questions():
    all_questions = parse_questions(resource_path("questions.txt"))
    # You can adjust the number of questions per quiz here
    num_questions = min(30, len(all_questions))
    return random.sample(all_questions, num_questions)
from utils import parse_questions, normalize_answer
import random
import json
import os
from datetime import datetime

@app.route('/')
def home():
    quiz_id = str(uuid.uuid4())  # 🔑 Create a unique ID
    questions = get_random_questions()
    question_cache[quiz_id] = questions  # 🗃️ Save to cache
    session['quiz_id'] = quiz_id  # 🧁 Store only the ID
    session['start_time'] = datetime.now().isoformat()
    return render_template('quiz.html', questions=questions)

@app.route('/submit', methods=['POST'])
def submit():
    quiz_id = session.get('quiz_id')
    questions = question_cache.get(quiz_id)

    if not questions:
        return redirect(url_for('home'))  # gracefully recover

    user_answers = {}
    score = 0
    results = []

    for idx, q in enumerate(questions):
        selected = request.form.getlist(f"q_{q['id']}")
        # Normalize all selected answers
        selected_norm = [normalize_answer(a) for a in selected]
        selected_set = set(selected_norm)
        user_answers[str(q['id'])] = list(selected_set)

        # Normalize correct answers
        correct_norm = [normalize_answer(a) for a in q.get('correct', [])]
        correct_set = set(correct_norm)

        # Debug info (remove after troubleshooting)
        print(f"Q{q['id']} selected: {selected_set}")
        print(f"Q{q['id']} correct: {correct_set}")

        # Fully correct: selected answers match correct answers exactly
        is_fully_correct = selected_set == correct_set
        if is_fully_correct:
            score += 1
        # Build answer details for template rendering
        answer_details = []
        for a in q['answers']:
            answer_text = normalize_answer(a if isinstance(a, str) else a['text'])
            answer_details.append({
                'text': a if isinstance(a, str) else a['text'],
                'is_correct': answer_text in correct_set,
                'is_selected': answer_text in selected_set
            })
        results.append({
            'question': q['question'],
            'answers': answer_details,
            'correct': list(correct_set),
            'selected': selected,
            'multi': q['multi'],
            'is_fully_correct': is_fully_correct
        })

    percent = round((score / len(questions)) * 100, 2)
    return render_template('results.html', results=results, percent=percent, score=score)

@app.route('/retake')
def retake():
    session.clear()
    return redirect(url_for('home'))

import webbrowser

if __name__ == '__main__':
    webbrowser.open("http://127.0.0.1:5000/")
    app.run(debug=True)

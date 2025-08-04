import uuid
from flask import Flask, render_template, request, redirect, url_for, session
from utils import parse_questions
import random
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Load questions and track served ones
QUESTIONS = parse_questions("questions.txt")
QUESTION_TRACK_FILE = "user_stats.json"
question_cache = {}  # 🎯 Our in-memory question store

if os.path.exists(QUESTION_TRACK_FILE):
    with open(QUESTION_TRACK_FILE, "r") as f:
        served_ids = json.load(f)
else:
    served_ids = []

def get_random_questions():
    pool = [q for q in QUESTIONS if q['id'] not in served_ids]
    needed = 30

    if len(pool) < needed:
        pool += QUESTIONS

    selected = random.sample(pool, needed)

    for q in selected:
        if q['id'] not in served_ids:
            served_ids.append(q['id'])

    with open(QUESTION_TRACK_FILE, "w") as f:
        json.dump(served_ids[:305], f)

    return selected

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

    for q in questions:
        selected = request.form.getlist(f"q_{q['id']}")
        user_answers[str(q['id'])] = selected

        correct_set = set(q['correct'])
        selected_set = set(selected)

        is_correct = correct_set == selected_set
        if is_correct:
            score += 1

        results.append({
            'question': q['question'],
            'answers': q['answers'],
            'correct': q['correct'],
            'selected': selected,
            'multi': q['multi'],
            'is_correct': is_correct
        })

    percent = round((score / len(questions)) * 100, 2)
    return render_template('results.html', results=results, percent=percent, score=score)

@app.route('/retake')
def retake():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

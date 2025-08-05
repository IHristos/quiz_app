import re
import re
def parse_questions(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()

    blocks = content.split("**[⬆ Back to Top](#table-of-contents)**")
    questions = []

    for idx, block in enumerate(blocks):
        block = block.strip()
        if not block:
            continue

        lines = block.split('\n')
        q_lines = [line for line in lines if not line.startswith('- [')]
        question_text = ' '.join(q_lines).strip()

        answers = []
        correct_answers = []

        for line in lines:
            match = re.match(r'- \[(x| )\] (.+)', line.strip())
            if match:
                checked, answer_text = match.groups()
                answers.append(answer_text.strip())
                if checked == 'x':
                    correct_answers.append(answer_text.strip())

        if question_text and answers:
            questions.append({
                'id': idx + 1,
                'question': question_text,
                'answers': answers,
                'correct': correct_answers,
                'multi': len(correct_answers) > 1
            })
    return questions

# Consistent normalization function
def normalize_answer(text):
    return text.strip().lower()

    return questions

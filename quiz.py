from flask import Flask, render_template, request, redirect, url_for, session
import csv
import random
import jsonpickle

app = Flask(__name__)
app.secret_key = 'sbdajhsb3423bjdjkjv3i4rrka'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

class Quiz:
    def __init__(self, filename):
        self.filename = filename
        self.questions = []
        self.score = 0
        self.num_questions = 0
        self.question_num = 0

    def load_questions(self, num):
        with open(self.filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            self.questions = random.choices(list(reader), k=num)

        self.num_questions = len(self.questions)

    def ask_question(self):
        question = self.questions[self.question_num][0]
        meanings = self.questions[self.question_num][1].split(';')
        #correct_answer = random.choice(meanings)
        correct_answer = meanings[0]
        options = [correct_answer]

        while len(options) < 5:
            option = random.choice(self.questions)[1].split(';')[0]
            if option not in options:
                options.append(option)

        random.shuffle(options)

        return question, options, correct_answer, self.num_questions

    def evaluate_answer(self, answer, options):
        question, _, correct_answer,_ = self.ask_question()
        self.question_num += 1
        print(answer)
        print(options)
        print(options[int(answer)-1])
        print(correct_answer)
        if options[int(answer)-1] == correct_answer:
            self.score += 1
            feedback = "Correct!"
        else:
            feedback = "Incorrect"

        if self.question_num >= self.num_questions:
            return question, feedback, correct_answer,True
        else:
            return question, feedback, correct_answer, False

    def run(self, num):
        self.load_questions(num)
        self.question_num = 0
        self.score = 0


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/start', methods=['GET', 'POST'])
def start():
    num = request.form.get('num_questions', type=int)
    quiz = Quiz('words.csv')
    quiz.run(num)
    session['quiz'] = jsonpickle.encode(quiz)
    return redirect(url_for('question', question_num=quiz.question_num))


@app.route('/question', methods=['GET', 'POST'])
def question():
    if 'quiz' not in session:
        return redirect(url_for('index'))
    quiz = jsonpickle.decode(session['quiz'])
    question, options, _, total_questions = quiz.ask_question()
    return render_template('question.html', question=question, options=options, question_num=quiz.question_num, total_questions=total_questions)


@app.route('/answer/<options>', methods=['GET', 'POST'])
def answer(options):
    options = options.split('&')
    if 'quiz' not in session:
        return redirect(url_for('index'))
    
    answer = request.form['answer']
    quiz = jsonpickle.decode(session['quiz'])
    question, feedback, correct_answer, end_of_quiz = quiz.evaluate_answer(answer, options)

    if end_of_quiz:
        #session.pop('quiz', None)
        return redirect(url_for('result'))
    else:
        session['quiz'] = jsonpickle.encode(quiz)
        return render_template('answer.html', question=question, options=options, feedback=feedback, correct_answer=correct_answer)


@app.route('/result', methods=['GET', 'POST'])
def result():
    if 'quiz' not in session:
        return redirect(url_for('index'))
    quiz = jsonpickle.decode(session['quiz'])
    score = quiz.score
    num_questions = quiz.num_questions
    session.pop('quiz', None)
    return render_template('result.html', score=score, num_questions=num_questions)


if __name__ == '__main__':
    app.run(debug=True, port=5000)

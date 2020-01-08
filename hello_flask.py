from flask import Flask, escape, request, render_template

from RackEvaluator import RackEvaluator, TileCondition

app = Flask(__name__)

@app.route('/')
def hello(title=None, report=""):

    compares = [("exactly","=="), ("less than","<"), ("greater than", ">"), ("at least", ">="), ("at most", "<=")]
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','?']

    title = "Q vs. Q"
    return render_template('index.html', title=title, compares = compares, alphabet =alphabet, report=report)

@app.route('/results', methods=['POST'])
def results():
    letter = request.form['DDLetter']
    count = int(request.form['DDCount'])
    compare = request.form['DDCompare']

    re = RackEvaluator([TileCondition(letter, count, compare)])
    axes, report = re.evaluate()    
    return hello(title="bozo", report = report.replace("\n", "<BR>"))


if __name__ == "__main__":
    app.run()
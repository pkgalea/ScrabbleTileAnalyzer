from flask import Flask, escape, request, render_template

from RackEvaluator import RackEvaluator, TileCondition

from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from bokeh.models import Span


import numpy as np

app = Flask(__name__)


@app.route('/')
def hello(title=None, report="", control=[1], test=[1]):

    control_hist, control_edges = np.histogram(control, density=True, bins=150)
    test_hist, test_edges = np.histogram(test, density=True, bins=150)
    fig = figure(plot_width=800, plot_height=600, tools="pan,wheel_zoom,box_zoom,reset", x_range=(-10, 150))
    fig.quad(top=control_hist, bottom=0, left=control_edges[:-1], right=control_edges[1:],
           fill_color="navy", line_color="white", alpha=0.5)
    fig.quad(top=test_hist, bottom=0, left=test_edges[:-1], right=test_edges[1:],
        fill_color="red", line_color="white", alpha=0.5)
    fig.xaxis.axis_label = 'x'
    fig.yaxis.axis_label = 'Pr(x)' 
    vline = Span(location=30, dimension='height', line_color='red', line_width=3)

    fig.renderers.extend([vline])

     
    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    script, div = components(fig)

    compares = [("exactly","=="), ("less than","<"), ("greater than", ">"), ("at least", ">="), ("at most", "<=")]
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','?']

    title = "Q vs. Q"
    return render_template('index.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources, 
        title=title, compares = compares, alphabet =alphabet, report=report)

@app.route('/results', methods=['POST'])
def results():
    letter = request.form['DDLetter']
    count = int(request.form['DDCount'])
    compare = request.form['DDCompare']

    re = RackEvaluator([TileCondition(letter, count, compare)])
    control, test, report = re.evaluate()    
    return hello(title="bozo", report = report.replace("\n", "<BR>"), control=control, test=test)


if __name__ == "__main__":
    app.run()
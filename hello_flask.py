from flask import Flask, escape, request, render_template

from src.RackEvaluator import RackEvaluator, TileCondition

from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from bokeh.models import Span

from collections import Counter



import numpy as np

app = Flask(__name__)



def createFigure(control, test):
    control_hist, control_edges = np.histogram(control, density=True, bins=np.max(control))
    test_hist, test_edges = np.histogram(test, density=True, bins=np.max(test))
    fig = figure(plot_width=600, plot_height=400, tools="pan,wheel_zoom,box_zoom,reset", x_range=(-10, 120))
    fig.quad(top=control_hist, bottom=0, left=control_edges[:-1], right=control_edges[1:],
           fill_color="navy", line_color="white", alpha=0.5)
    fig.quad(top=test_hist, bottom=0, left=test_edges[:-1], right=test_edges[1:],
        fill_color="red", line_color="white", alpha=0.5)
    fig.xaxis.axis_label = 'score'
    fig.yaxis.axis_label = 'Density' 
    fig.legend.location = "top_right"
    fig.legend.click_policy="hide"
 
    vline = Span(location=30, dimension='height', line_color='red', line_width=3)
    fig.renderers.extend([vline])
    return fig


@app.route('/')
def hello(rack_eval=None):

    compares = [("exactly","=="), ("at least", ">="), ("at most", "<=")]
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','?']

    if (not rack_eval):
        return render_template('index.html', has_data=False, compares = compares, alphabet = alphabet)

    fig = createFigure(rack_eval.control_y, rack_eval.test_y)
     
    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    script, div = components(fig)

    if (rack_eval.p_value >= 0.001):
        p_value_formatted = "{0:.2f}".format(rack_eval.p_value)
    else:
        p_value_formatted = "{0:.2E}".format(rack_eval.p_value)
    ci_lower_formatted = "{0:.3f}".format(rack_eval.ci_lower)
    ci_upper_formatted = "{0:.3f}".format(rack_eval.ci_upper)

    return render_template('index.html',
        has_data = True,
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources, 
        compares = compares, 
        alphabet =alphabet,
        control_label = rack_eval.control_label,   
        test_label = rack_eval.test_label,
        control_n = rack_eval.control_n,
        test_n = rack_eval.test_n,
        control_y_bar = rack_eval.control_y_bar,
        test_y_bar = rack_eval.test_y_bar,
        p_value = rack_eval.p_value,
        p_value_formatted = p_value_formatted,
        ci_lower_formatted = ci_lower_formatted,
        ci_upper_formatted = ci_upper_formatted
       
        )

@app.route('/results', methods=['POST'])
def results():
    letterC = request.form['DDLetterC']
    countC = int(request.form['DDCountC'])
    compareC = request.form['DDCompareC']

    letterT = request.form['DDLetterT']
    countT = int(request.form['DDCountT'])
    compareT = request.form['DDCompareT']


    rack_eval = RackEvaluator([TileCondition(letterC, countC, compareC)], [TileCondition(letterT, countT, compareT)])
    if rack_eval.evaluate():           
        return hello(rack_eval)
    return hello("no")


if __name__ == "__main__":
    app.run()
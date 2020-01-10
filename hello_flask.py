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



def createFigure(control, test, control_label, test_label):

    control_hist, control_edges = np.histogram(control, density=True, bins=np.max(control))
    test_hist, test_edges = np.histogram(test, density=True, bins=np.max(test))
 
    fig = figure(plot_width=600, plot_height=400, tools="pan,wheel_zoom,box_zoom,reset", x_range=(-10, 120))
    fig.quad(top=control_hist, bottom=0, left=control_edges[:-1], right=control_edges[1:],
           fill_color="navy", line_color="white", alpha=0.5, legend="Control: " + control_label)
    fig.quad(top=test_hist, bottom=0, left=test_edges[:-1], right=test_edges[1:],
        fill_color="red", line_color="white", alpha=0.5, legend="Test: " + test_label)
    max_y = max([np.max(test_hist), np.max(control_hist)])
    fig.line([np.mean(control), np.mean(control)], [0, max_y], legend="Control mean ({0:.2f})".format(np.mean(control)),line_dash=[4, 4], color="navy", line_width=3)
    fig.line([np.mean(test), np.mean(test)], [0, max_y], legend="Test mean ({0:.2f})".format(np.mean(test)),line_dash=[4, 4], color="red", line_width=3)
    fig.xaxis.axis_label = 'Turn Score'
    fig.yaxis.axis_label = 'Density' 
    fig.legend.location = "top_right"
    fig.legend.click_policy="hide"
    fig.xaxis.axis_label_text_font_size = '15pt'
    fig.yaxis.axis_label_text_font_size = '15pt'
    fig.title.text = "Turn Scores for Control and Test Groups"
    fig.title.text_font_size = "25px"
    return fig
 


@app.route('/')
def hello(rack_eval=None):

    compares = [("exactly","=="), ("at least", ">="), ("at most", "<=")]
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','?']
    
    if (not rack_eval):
        return render_template('index.html', has_data=False, bad_data=False, compares = compares, alphabet = alphabet)
    if (rack_eval.control_n < 40 or rack_eval.test_n < 40):
        return render_template('index.html', bad_data = True, has_data=False, compares = compares, alphabet = alphabet)

    fig = createFigure(rack_eval.control_y, rack_eval.test_y, rack_eval.control_label, rack_eval.test_label)
     
    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()

    # render template
    script, div = components(fig)

    if (rack_eval.p_value >= 0.001):
        p_value_formatted = "{0:.2f}".format(rack_eval.p_value)
    else:
        p_value_formatted = "{0:.2E}".format(rack_eval.p_value)
    ci_lower_formatted = "{0:.2f}".format(rack_eval.ci_lower)
    ci_upper_formatted = "{0:.2f}".format(rack_eval.ci_upper)
    mean_diff_formatted = "{0:.2f}".format(rack_eval.mean_diff)

    return render_template('index.html',
        has_data = True,
        bad_data = False, 
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
        ci_upper_formatted = ci_upper_formatted,
        mean_diff = mean_diff_formatted
       
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
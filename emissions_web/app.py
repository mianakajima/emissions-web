from flask import Flask, render_template
from werkzeug.exceptions import abort
import pandas as pd
import json
import plotly
import plotly.express as px
from helpers.caiso_helpers import *

app = Flask(__name__)

emissions_rate = {
    'Biomass_CO2': 81.7,
    'Geothermal_CO2': 152.849,
    ''
}

@app.route('/')
def index():
    df = get_supply_trend_today()
    fig = px.line(df, x = 'DateTime', y = 'value', color = 'variable')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('index.html', graphJSON=graphJSON)
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
    'Geothermal_CO2': 152.849
}

@app.route('/')
def index():
    df = get_supply_trend_today()

    #plot all supply
    df_long = pd.melt(df, id_vars=['DateTime'])
    fig = px.line(df_long, x = 'DateTime', y = 'value', color = 'variable')
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    #plot percent renewable

    per_renewable = get_percentage_renewable(df)
    fig2 = px.line(per_renewable, x = 'DateTime', y = 'RenewablePercentage')
    graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    current_percentage = round(per_renewable.RenewablePercentage.iloc[per_renewable.shape[0] - 1], 2)

    return render_template('index.html', graphJSON=graphJSON, graphJSON2 = graphJSON2, current_percentage = current_percentage)
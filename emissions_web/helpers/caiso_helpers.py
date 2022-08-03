from datetime import date
import requests
from io import StringIO
import pandas as pd

def get_supply_trend_today():
    """Get today's supply trend from CAISO website. """

    #retrieve data
    url = 'https://www.caiso.com/outlook/SP/fuelsource.csv'
    r = requests.get(url)

    data_io = StringIO(r.text)
    df = pd.read_csv(data_io, sep = ",")

    # clean datetime
    today = date.today()
    df['DateTime'] = pd.to_datetime(str(today) + ' ' + df['Time'])

    df.drop('Time', axis = 1, inplace = True)

    df_long = pd.melt(df, id_vars = ['DateTime'])

    return df_long
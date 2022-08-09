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

    #df_long = pd.melt(df, id_vars = ['DateTime'])

    return df

def get_percentage_renewable(df):
    """Return df with percentage of load served by non GHG-producing energy sources."""

    df_new = df.copy()
    df_new['Renewables'] = df['Solar'] + df['Wind'] + df['Small hydro'] + df['Nuclear'] + df['Large Hydro']
    df_new['Total'] = df.drop('DateTime', axis = 1).sum(axis = 1)
    df_new['RenewablePercentage'] = 100*df_new['Renewables']/df_new['Total']

    return df_new

from datetime import date

import pandas
import requests
from io import StringIO
import pandas as pd
import zipfile
import xml.etree.ElementTree as ET
import re
import os

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

def get_oasis_forecast(start_date, end_date, market_run_id, data_item):
    """Returns OASIS API call as pandas dataframe
    For data_item:
    - 'ENE_SLRS': Generation
    - 'SLD_REN_FCST': Solar and Wind Forecast sol

    """

    url = f"http://oasis.caiso.com/oasisapi/SingleZip?queryname={data_item}&" \
                    f"startdatetime={start_date}T07:00-0000&" \
                    f"enddatetime={end_date}T07:00-0000&version=1&" \
                    f"market_run_id={market_run_id}"
    # Make request and unzip file
    r = requests.get(url)

    # extract zipfile
    with open('./temp_zip.zip', 'wb') as code:
        code.write(r.content)

    with zipfile.ZipFile('./temp_zip.zip', 'r') as zip_ref:
        zip_ref.extractall('./download_data')

    # get name of XML file
    header_filename = r.headers['Content-Disposition']
    zip_file = re.sub('inline; filename=', '', header_filename)
    xml_file = re.sub('.zip;', '.xml', zip_file)
    os.remove('temp_zip.zip')
    # parse XML file

    xml_data = ET.parse(f"download_data/{xml_file}")
    root = xml_data.getroot()

    # set of unique tags in file
    tags = {elem.tag for elem in root.iter()}

    data_to_collect = {'value': 'VALUE',
                       'start_date': 'INTERVAL_START_GMT',
                       'end_date': 'INTERVAL_END_GMT',
                       'trading_hub': 'TRADING_HUB',
                       'ren_type': 'RENEWABLE_TYPE',
                       'resource_name': 'RESOURCE_NAME',
                       'data_item': 'DATA_ITEM'}

    data_collected = {}

    for value in data_to_collect:
        tag = f'{{http://www.caiso.com/soa/OASISReport_v1.xsd}}{data_to_collect[value]}'
        if tag in tags:
            data_collected[value] = [repdata.text for repdata in root.iter(tag)]

    df = pandas.DataFrame(data_collected)


    return df
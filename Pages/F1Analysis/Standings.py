import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as rq

@st.cache_resource(show_spinner=False)
def get_driver_standings():
    url = "https://www.formula1.com/en/results/2024/drivers"
    response = rq.get(url).text
    soup = bs(response, 'html.parser')
    table = soup.find('table', class_='f1-table-with-data')

    headers = []
    rows = []

    for th in table.find_all('th'):
        headers.append(th.text.strip())

        
    for tr in table.find_all('tr'):
        cells = tr.find_all('td')
        if len(cells) > 0:
            row = [cell.text.strip() for cell in cells]
            rows.append(row)

    df = pd.DataFrame(rows, columns=headers)
    df["Driver"] = df['Driver'].apply(lambda x: x[:-3])

    df = df.drop(columns=["Nationality"])

    return df

@st.cache_resource(show_spinner=False)
def get_contructor_standings():
    url = "https://www.formula1.com/en/results/2024/team"
    response = rq.get(url).text
    soup = bs(response, 'html.parser')
    table = soup.find('table', class_='f1-table-with-data')

    headers = []
    rows = []

    for th in table.find_all('th'):
        headers.append(th.text.strip())

    for tr in table.find_all('tr'):
        cells = tr.find_all('td')
        if len(cells) > 0:
            row = [cell.text.strip() for cell in cells]
            rows.append(row)
    
    df = pd.DataFrame(rows, columns=headers)

    return df
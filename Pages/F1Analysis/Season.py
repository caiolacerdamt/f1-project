import streamlit as st
import pandas as pd
import numpy as np
import tensorflow as tf
import requests as rq
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from fastf1 import get_events_remaining
import time
from io import BytesIO
from PIL import Image

@st.cache_data(show_spinner=False)
def load_predictions():
    model = tf.keras.models.load_model('model/model.keras')
    df_to_predict = pd.read_csv("data/current_df_to_predict.csv")
    df_encoder_combination = pd.read_csv("data/df_model.csv")
    df_encoder_combination = df_encoder_combination[["FullName", "NameEncoder"]].drop_duplicates().sort_values(by='NameEncoder')
    predicition = model.predict(df_to_predict)
    df_encoder_combination["Probabilities (%)"] = np.round(predicition * 100, 2)
    df_encoder_combination = df_encoder_combination.sort_values(by="Probabilities (%)", ascending=False)
    df_encoder_combination['Probabilities (%)'] = df_encoder_combination['Probabilities (%)'].astype(str)
    top5 = df_encoder_combination[["FullName", "Probabilities (%)"]].iloc[:5]

    return top5

@st.cache_resource(show_spinner=False)
def get_next_race_content():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    url = "https://www.formula1.com/en/racing/2024"
    driver.get(url)
    time.sleep(5)
    html = driver.page_source
    soup = bs(html, 'html.parser')
    content_divs = soup.find_all('div', attrs={'class': 'f1-container'})
    return content_divs 

@st.cache_resource(show_spinner=False)
def get_specific_div_content():
    content_div = get_next_race_content()
    country_event = get_events_remaining().iloc[0].Country
    for div in content_div:
        if div.find('fieldset') and country_event in div.text:
            event_content = div
            break
    return event_content

@st.cache_resource(show_spinner=False)
def get_next_race_times():
    next_race = get_events_remaining().iloc[0].drop(labels=["RoundNumber", "Country", "Location", "OfficialEventName", "EventDate",
                                                            "EventName", "EventFormat", "Session1Date", "Session2Date", 
                                                            "Session3Date", "Session4Date", "Session5Date", "F1ApiSupport"])
        
    sessions = []
    dates = []
    hours = []

    for i in range(1, 6):
        session_name = next_race[f'Session{i}']
        session_datetime = pd.to_datetime(next_race[f'Session{i}DateUtc'])

        sessions.append(session_name)
        dates.append(session_datetime.strftime('%m-%d'))
        hours.append(session_datetime.strftime('%H:%M'))

    df = pd.DataFrame({
        'Session': sessions,
        'Date': dates,
        'Hour': hours
    })

    return df

@st.cache_data(show_spinner=False)
def get_flag_and_circuit_images():
    div_event_content = get_specific_div_content()
    country_name = get_events_remaining().iloc[0].Country
    country_flag = div_event_content.find('img', alt=country_name)
    country_flag_url = country_flag['src'] if country_flag else None

    circuirt_img = div_event_content.find('img', alt=lambda value: value and 'circuit' in value.lower())
    circuirt_url = circuirt_img['src'] if circuirt_img else None
 
    return country_name, country_flag_url, circuirt_url

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

    return df


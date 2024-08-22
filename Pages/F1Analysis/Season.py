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
    #subprocess.run(['python', 'script_model.py'], check=True)
    model = tf.keras.models.load_model('model/model.keras')
    df_to_predict = pd.read_csv("data/current_df_to_predict.csv")
    df_encoder_combination = pd.read_csv("data/df_model.csv")
    df_encoder_combination = df_encoder_combination[["FullName", "NameEncoder"]].drop_duplicates().sort_values(by="NameEncoder")
    predicition = model.predict(df_to_predict)
    df_encoder_combination["Probabilities"] = np.round(predicition * 100, 2)
    df_encoder_combination = df_encoder_combination.sort_values(by="Probabilities", ascending=False)
    df_encoder_combination['Probabilities'] = df_encoder_combination['Probabilities'].astype(str)
    top5 = df_encoder_combination[["FullName", "Probabilities"]].iloc[:5]

    return top5

@st.cache_data(show_spinner=False)
def initialize_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

@st.cache_data(show_spinner=False)
def get_next_race_content():
    driver = initialize_chrome_driver()
    url = "https://www.formula1.com/en/racing/2024"
    driver.get(url)
    time.sleep(5)
    html = driver.page_source
    soup = bs(html, 'html.parser')
    content_divs = soup.find_all('div', attrs={'class': 'f1-container'})
    return content_divs    

@st.cache_data(show_spinner=False)
def get_specific_div_content():
    content_div = get_next_race_content()
    country_event = get_events_remaining().iloc[0].Country
    for div in content_div:
        if div.find('fieldset') and country_event in div.text:
            event_content = div
            break
    return event_content

@st.cache_data(show_spinner=False)
def get_date_events():
    event_content = get_specific_div_content()
    paragraphs = event_content.find_all('p', class_='f1-text')
    titles = event_content.find_all('p', class_='f1-heading')
    event_dates = []
    event_titles = []
    for p in paragraphs:
        if 'font-normal' in p.get('class', []) and 'uppercase' in p.get('class', []):
            event_dates.append(p.get_text())
    for p in titles:
        if 'uppercase' in p.get('class', []):
           event_titles.append(p.get_text())
    return event_dates, event_titles

@st.cache_data(show_spinner=False)
def create_event_dataframe():
    dates, titles = get_date_events()
    event_data = []
    for i in range(len(titles)):
        event_data.append({
            'Event': titles[i],
            'Day': dates[i * 2],
            'Time': dates[i * 2 + 1]
        })

    df = pd.DataFrame(event_data)

    return df

@st.cache_data(show_spinner=False)
def get_flag_and_circuit_images():
    div_event_content = get_specific_div_content()
    images = div_event_content.find_all('img')[:2]
    img_list = []
    for image in images:
        img_url = image['src']
        response = rq.get(img_url)
        img = Image.open(BytesIO(response.content))
        img_list.append(img)
    return img_list

@st.cache_data(show_spinner=False)
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


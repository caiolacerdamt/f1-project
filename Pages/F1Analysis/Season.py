import streamlit as st
import fastf1 as ff1
import pandas as pd
import numpy as np
import pytz
from PIL import Image, ImageDraw
import tensorflow as tf

@st.cache_data
def load_predictions():
    #subprocess.run(['python', 'script_model.py'], check=True)
    model = tf.keras.models.load_model('../../model/model.keras')
    df_to_predict = pd.read_csv("../../data/current_df_to_predict.csv")
    df_encoder_combination = pd.read_csv("../../data/df_model.csv")
    df_encoder_combination = df_encoder_combination[["FullName", "NameEncoder"]].drop_duplicates().sort_values(by="NameEncoder")
    predicition = model.predict(df_to_predict)
    np.set_printoptions(suppress=True)
    probabilities = np.round(predicition * 100, 2)
    df_encoder_combination["Probabilities"] = probabilities
    df_encoder_combination = df_encoder_combination.sort_values(by="Probabilities", ascending=False)
    top3 = df_encoder_combination[["FullName", "Probabilities"]].iloc[:3]

    return top3["FullName"].tolist(), top3["Probabilities"].tolist()

@st.cache_data
def get_and_process_next_race_sessions(backend='fastf1', timezone='UTC', target_timezone='America/Sao_Paulo'):
    race = ff1.get_events_remaining(backend=backend)
    next_race_sessions = race[["Country","EventName", "Session1", "Session1DateUtc", "Session2", "Session2DateUtc", "Session3", "Session3DateUtc", "Session4", "Session4DateUtc", "Session5", "Session5DateUtc"]].iloc[0]
    next_race_sessions = pd.DataFrame([next_race_sessions])
    
    columns_to_exclude = ["Country","EventName", "Session1", "Session2", "Session3", "Session4", "Session5"]
    brt = pytz.timezone(target_timezone)

    def process_datetime_columns(df, timezone='UTC'):
        df_processed = df.copy()
        for column in df_processed.columns:
            if column not in columns_to_exclude:
                df_processed[column] = pd.to_datetime(df_processed[column], errors='coerce')
                df_processed[column] = df_processed[column].fillna(df[column])
                if df_processed[column].dt.tz is None:
                    df_processed[column] = df_processed[column].dt.tz_localize(timezone)
                df_processed[column] = df_processed[column].dt.tz_convert(brt)
        return df_processed

    next_race_sessions_df = process_datetime_columns(next_race_sessions)
    return next_race_sessions_df

def display_next_race_sessions():
    next_race_sessions_df = get_and_process_next_race_sessions()

    event_name = next_race_sessions_df["EventName"].iloc[0]
    country_name = next_race_sessions_df["Country"].iloc[0]
    st.write(f"""<div style='text-align: center; width: 100; font-size:20px;'>
                {event_name} - {country_name}
             </>""", unsafe_allow_html=True)
    for column in next_race_sessions_df.columns:
        if column != "EventName":
            if pd.api.types.is_datetime64_any_dtype(next_race_sessions_df[column]):
                data_column = next_race_sessions_df[column]
                day = data_column.dt.day
                month = data_column.dt.month
                year = data_column.dt.year
                hour = data_column.dt.hour
                minute = data_column.dt.minute

                d = day.iloc[0]
                m = month.iloc[0]
                y = year.iloc[0]
                h = hour.iloc[0]
                min = minute.iloc[0]
                formatted_time = f"{h:02}:{min:02}"

                session_name = next_race_sessions_df[column.replace('DateUtc', '')].iloc[0]

                st.write(f"""
                <div style='text-align: center; width: 100%; font-size:20px;'>
                    {session_name} - {d}/{m}/{y} - {formatted_time}
                </div>
                """, unsafe_allow_html=True)

def plot_circuit():
    next_race = ff1.get_events_remaining().iloc[0].EventName
    session = ff1.get_session(2023, next_race, 'Q')
    session.load()

    lap = session.laps.pick_fastest()
    tel = lap.get_telemetry()
    x = np.array(tel['X'].values)
    y = np.array(tel['Y'].values)

    x_min, x_max = x.min(), x.max()
    y_min, y_max = y.min(), y.max()
    x = (x - x_min) / (x_max - x_min) * 170
    y = (y - y_min) / (y_max - y_min) * 170

    img_width, img_height = 200, 200
    img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    line_points = list(zip(y, x))
    draw.line(line_points, fill='white', width=2)

    img = img.rotate(200, expand=True)
    img
    return img
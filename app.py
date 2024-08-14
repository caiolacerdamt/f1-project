import streamlit as st
import fastf1 as ff1
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np
import pytz
from PIL import Image, ImageDraw
import tensorflow as tf
import subprocess

@st.cache_data
def get_circuits(year):
    with st.spinner("Carregando Circuitos - Isso pode levar alguns minutos"):
        if year:
            schedule = ff1.get_event_schedule(year)["EventName"].unique()
            return list(schedule)
        return []

@st.cache_data
def get_pilots(year, circuit):
    if year and circuit:
        race = ff1.get_session(year, circuit, "R")
        race.load()
        drivers = race._drivers_from_f1_api()
        drivers_df = pd.DataFrame(drivers[["Abbreviation", "FullName"]])
        laps = list(range(1, race._total_laps + 1))
        return drivers_df, race, laps
    return pd.DataFrame(columns=["Abbreviation", "FullName"]), None

@st.cache_data
def load_predictions():
    #subprocess.run(['python', 'script_model.py'], check=True)
    model = tf.keras.models.load_model('model/model.keras')
    df_to_predict = pd.read_csv("current_df_to_predict.csv")
    df_encoder_combination = pd.read_csv("df_model.csv")
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

    img_rotated = img.rotate(200, expand=True)
    img_rotated
    return img_rotated

def plotting_graph1(df1, df2, option_piloto1, option_piloto2):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df1['Distance'], y=df1['Speed'], mode='lines', name=option_piloto1))
    fig.add_trace(go.Scatter(x=df2['Distance'], y=df2['Speed'], mode='lines', name=option_piloto2))
    fig.update_layout(title='Distância x Velocidade', xaxis_title='Distância (m)', yaxis_title='Velocidade (km/h)', template='plotly_dark')
    return fig

def plotting_graph2(df1, df2, option_piloto1, option_piloto2):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df1['Distance'], y=df1['Throttle'], mode='lines', name=option_piloto1))
    fig.add_trace(go.Scatter(x=df2['Distance'], y=df2['Throttle'], mode='lines', name=option_piloto2))
    fig.update_layout(title='Distância x Aceleração', xaxis_title='Distância (m)', yaxis_title='Aceleração', template='plotly_dark')
    return fig

def plotting_graph3(df1, df2, option_piloto1, option_piloto2):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df1['Distance'], y=df1['nGear'], mode='lines', name=option_piloto1))
    fig.add_trace(go.Scatter(x=df2['Distance'], y=df2['nGear'], mode='lines', name=option_piloto2))
    fig.update_layout(title='Distância x Marcha', xaxis_title='Distância (m)', yaxis_title='Marcha', template='plotly_dark')
    return fig

st.set_page_config(layout="wide")
col1, col2 = st.columns(2, gap="medium")

anos = list(range(2018, 2025))
option_ano = None
option_circuito = None
option_piloto1 = None
option_piloto2 = None
option_laps = None

with col1:
    option_ano = st.selectbox("Escolha o ano", anos, index=None)

if option_ano is not None:
    with col1:
        with st.spinner("Carregando Circuitos"):
            circuits = get_circuits(option_ano)
            option_circuito = st.selectbox("Circuito", circuits, index=None, placeholder="Escolha um circuito")

if option_ano is not None and option_circuito is not None:
    try:
        with col1:
            with st.spinner("Carregando Dados"):
                pilotos, race, laps = get_pilots(option_ano, option_circuito)
                option_piloto1 = st.selectbox("Piloto 1", pilotos["FullName"].tolist(), index=None, placeholder="Escolha um piloto")
                option_piloto2 = st.selectbox("Piloto 2", pilotos["FullName"].tolist(), index=None, placeholder="Escolha um piloto")
                option_laps = st.selectbox("Volta", laps, index=None, placeholder="Escolha uma volta")
    except Exception as e:
        st.error("Corrida não concluída ainda")

if option_piloto1 is not None and option_piloto2 is not None and option_laps is not None:
    with col1:
        show_graphs = st.button("Mostrar Gráficos")
    
        if show_graphs:
            abbreviation1 = pilotos.loc[pilotos["FullName"] == option_piloto1, "Abbreviation"].iloc[0]
            abbreviation2 = pilotos.loc[pilotos["FullName"] == option_piloto2, "Abbreviation"].iloc[0]
            df1 = race.laps.pick_driver(abbreviation1).pick_lap(option_laps).get_car_data().add_distance()
            df2 = race.laps.pick_driver(abbreviation2).pick_lap(option_laps).get_car_data().add_distance()

            col1.subheader(f"Gráficos de telemetria {option_piloto1} x {option_piloto2} - {option_circuito} {option_ano}")
            col1.plotly_chart(plotting_graph1(df1, df2, option_piloto1, option_piloto2))
            col1.plotly_chart(plotting_graph2(df1, df2, option_piloto1, option_piloto2))
            col1.plotly_chart(plotting_graph3(df1, df2, option_piloto1, option_piloto2))

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    body {
        font-family: 'Roboto', sans-serif;
    }
    div {
        font-family: 'Roboto', sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)

with col2:
    next_race = 'Next Race Info'
    st.markdown(f"""
        <div style='text-align:center; font-size:24px; font-weight:bold;'>{next_race}</div>
        """, unsafe_allow_html=True)
    next_race_col1, next_race_col2 = st.columns(2)
    with next_race_col1:
        display_next_race_sessions()
    with next_race_col2:
        plot_circuit()
    names, probs = load_predictions()
    st.write("Top 3 Probabilities to Winner")
    for name, prob in zip(names, probs):
        st.write(f"{name} - {prob:.2f}%")
     

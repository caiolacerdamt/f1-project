import streamlit as st
import fastf1 as ff1
import pandas as pd
import plotly.graph_objects as go
import time

def get_circuits(year):
    with st.spinner("Loading"):
        if year is not None:
            schedule = ff1.get_event_schedule(year)["EventName"].unique()
            return list(schedule)
        else:
            return []

def get_pilots(year, circuit):
    with st.spinner("Loading"):
        if (year is not None) and (circuit is not None):
            race = ff1.get_session(year, circuit, "R")
            race.load()
            drivers = race._drivers_from_f1_api()
            drivers_df = pd.DataFrame(drivers[["Abbreviation", "FullName"]])
            return drivers_df, race
        else: 
            return pd.DataFrame(columns=["Abbreviation", "FullName"]), None

def get_numbers_of_laps(race):
    if race is not None:
        return list(range(1, race._total_laps + 1))
    else:
        return []

def plotting_graph(df1, df2, option_piloto1, option_piloto2):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df1['Distance'], y=df1['Speed'], mode='lines', name=option_piloto1))
    fig.add_trace(go.Scatter(x=df2['Distance'], y=df2['Speed'], mode='lines', name=option_piloto2))
    fig.update_layout(
        title=f'Comparação de Telemetria - {option_piloto1} x {option_piloto2}',
        xaxis_title='Distância (m)',
        yaxis_title='Velocidade (km/h)',
        template='plotly_dark'
    )
    return fig

st.set_page_config(layout="wide")

col1, col2 = st.columns(2)
anos = list(range(2018, 2025))

with col1:
    with st.spinner("Loading"):
        option_ano = st.selectbox(
            "Escolha o ano", 
            anos)

if option_ano is not None:
    circuits = get_circuits(option_ano)
    with col2:
        option_circuito = st.selectbox(
            "Circuito", 
            circuits, 
            placeholder="Escolha um circuito")

if option_ano is not None and option_circuito is not None:
    pilotos, race = get_pilots(option_ano, option_circuito)
    col1, col2 = st.columns(2)
    with col1:
        option_piloto1 = st.selectbox(
            "Piloto 1", 
            pilotos["FullName"].tolist(),
            placeholder="Escolha um piloto")
    with col2:
        option_piloto2 = st.selectbox(
            "Piloto 2", 
            pilotos["FullName"].tolist(), 
            placeholder="Escolha um piloto")

    if race is not None:
        laps = get_numbers_of_laps(race)
        option_lap = st.selectbox(
            "Volta", 
            laps, 
            placeholder="Escolha a volta")

if st.button('Mostrar Gráfico de Telemetria'):
    with st.spinner("Carregando"):
        if race is not None and option_piloto1 and option_piloto2 and option_lap:
            abbreviation1 = pilotos.loc[pilotos["FullName"] == option_piloto1, "Abbreviation"].iloc[0]
            abbreviation2 = pilotos.loc[pilotos["FullName"] == option_piloto2, "Abbreviation"].iloc[0]

            df1 = race.laps.pick_driver(abbreviation1).pick_lap(option_lap).get_car_data().add_distance()
            df2 = race.laps.pick_driver(abbreviation2).pick_lap(option_lap).get_car_data().add_distance()

            fig = plotting_graph(df1, df2, option_piloto1, option_piloto2)
            st.plotly_chart(fig)

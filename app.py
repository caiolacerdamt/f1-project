import streamlit as st
import fastf1 as ff1
import pandas as pd
import plotly.graph_objects as go
import time

def get_circuits(year):
    with st.spinner("Carregando Circuitos - Isso pode levar alguns minutos"):
        if year is not None:
            schedule = ff1.get_event_schedule(year)["EventName"].unique()
            return list(schedule)
        else:
            return []

def get_pilots(year, circuit):
    #with st.spinner("Carregando dados da corrida, isso pode levar alguns minutos"):
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

def plotting_graph1(df1, df2, option_piloto1, option_piloto2):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df1['Distance'], y=df1['Speed'], mode='lines', name=option_piloto1))
    fig.add_trace(go.Scatter(x=df2['Distance'], y=df2['Speed'], mode='lines', name=option_piloto2))
    fig.update_layout(
        title=f'Distância x Velocidade',
        xaxis_title='Distância (m)',
        yaxis_title='Velocidade (km/h)',
        template='plotly_dark'
    )
    return fig

def plotting_graph2(df1, df2, option_piloto1, option_piloto2):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df1['Distance'], y=df1['Throttle'], mode='lines', name=option_piloto1))
    fig.add_trace(go.Scatter(x=df2['Distance'], y=df2['Throttle'], mode='lines', name=option_piloto2))
    fig.update_layout(
        title=f'Distância x Aceleração',
        xaxis_title='Distância (m)',
        yaxis_title='Aceleração',
        template='plotly_dark'
    )
    return fig

def plotting_graph3(df1, df2, option_piloto1, option_piloto2):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df1['Distance'], y=df1['nGear'], mode='lines', name=option_piloto1))
    fig.add_trace(go.Scatter(x=df2['Distance'], y=df2['nGear'], mode='lines', name=option_piloto2))
    fig.update_layout(
        title=f'Distância x Marcha',
        xaxis_title='Distância (m)',
        yaxis_title='Marcha',
        template='plotly_dark'
    )
    return fig

st.set_page_config(layout="wide")

col1, col2 = st.columns(2)
anos = list(range(2018, 2025))

with col1:
    option_ano = st.selectbox(
        "Escolha o ano", 
        anos,
        index=None,)

if option_ano is not None:
    circuits = get_circuits(option_ano)
    with col1:
        option_circuito = st.selectbox(
            "Circuito", 
            circuits,
            index=None,
            placeholder="Escolha um circuito")

if option_ano is not None and option_circuito is not None:
    try:
        with col1:
            pilotos, race = get_pilots(option_ano, option_circuito)
        with col1:
            option_piloto1 = st.selectbox(
                "Piloto 1", 
                pilotos["FullName"].tolist(),
                index=None,
                placeholder="Escolha um piloto")
        with col1:
            option_piloto2 = st.selectbox(
                "Piloto 2", 
                pilotos["FullName"].tolist(), 
                index=None,
                placeholder="Escolha um piloto")

            if race is not None:
                with col1:
                    laps = get_numbers_of_laps(race)
                    option_lap = st.selectbox(
                        "Volta", 
                        laps,
                        index=None,
                        placeholder="Escolha a volta")
    except Exception as e:
        col1.error("Corrida não concluída ainda")

    if col1.button("Mostrar Gráfico"):
        if race is not None and option_piloto1 and option_piloto2 and option_lap:
            try:
                abbreviation1 = pilotos.loc[pilotos["FullName"] == option_piloto1, "Abbreviation"].iloc[0]
                abbreviation2 = pilotos.loc[pilotos["FullName"] == option_piloto2, "Abbreviation"].iloc[0]

                df1 = race.laps.pick_driver(abbreviation1).pick_lap(option_lap).get_car_data().add_distance()
                df2 = race.laps.pick_driver(abbreviation2).pick_lap(option_lap).get_car_data().add_distance()

                col1.title(f"Gráficos de telemetria {option_piloto1} x {option_piloto2} - {option_circuito} {option_ano}")

                fig = plotting_graph1(df1, df2, option_piloto1, option_piloto2)
                col1.plotly_chart(fig)
                fig = plotting_graph2(df1, df2, option_piloto1, option_piloto2)
                col1.plotly_chart(fig)
                fig = plotting_graph3(df1, df2, option_piloto1, option_piloto2)
                col1.plotly_chart(fig)
            except Exception as e:
                col1.error(f"""Erro ao carregar telemetria:
                        Piloto não concluiu a volta 
                        """)

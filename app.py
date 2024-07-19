import streamlit as st
import fastf1 as ff1
import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import numpy as np
import pytz

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
def get_and_process_next_race_sessions(backend='fastf1', timezone='UTC', target_timezone='America/Sao_Paulo'):
    race = ff1.get_events_remaining(backend=backend)
    next_race_sessions = race[["EventName", "Session1", "Session1DateUtc", "Session2", "Session2DateUtc", "Session3", "Session3DateUtc", "Session4", "Session4DateUtc", "Session5", "Session5DateUtc"]].iloc[0]
    next_race_sessions = pd.DataFrame([next_race_sessions])
    
    columns_to_exclude = ["EventName", "Session1", "Session2", "Session3", "Session4", "Session5"]
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

def display_next_race_sessions(col):
    next_race_sessions_df = get_and_process_next_race_sessions()

    with col:
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

                    st.write(f"{session_name} - {d}/{m}/{y} - {formatted_time}")

def plot_circuit():
    session = ff1.get_session(2021, "Austrian Grand Prix", 'Q')
    session.load()
    lap = session.laps.pick_fastest()
    tel = lap.get_telemetry()
    x = np.array(tel['X'].values)
    y = np.array(tel['Y'].values)
    
    fig, ax = plt.subplots(figsize=(10, 2))
    ax.plot(x, y, color='white', linewidth=2)
    ax.axis('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    return fig

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
col1, col2 = st.columns(2, gap="medium", vertical_alignment="center")
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



        # if st.button("Mostrar Gráfico"):
        #     if race and option_piloto1 and option_piloto2 and option_lap:
        #         try:
        #             abbreviation1 = pilotos.loc[pilotos["FullName"] == option_piloto1, "Abbreviation"].iloc[0]
        #             abbreviation2 = pilotos.loc[pilotos["FullName"] == option_piloto2, "Abbreviation"].iloc[0]
        #             df1 = race.laps.pick_driver(abbreviation1).pick_lap(option_lap).get_car_data().add_distance()
        #             df2 = race.laps.pick_driver(abbreviation2).pick_lap(option_lap).get_car_data().add_distance()

        #             col1.title(f"Gráficos de telemetria {option_piloto1} x {option_piloto2} - {option_circuito} {option_ano}")
        #             col1.plotly_chart(plotting_graph1(df1, df2, option_piloto1, option_piloto2))
        #             col1.plotly_chart(plotting_graph2(df1, df2, option_piloto1, option_piloto2))
        #             col1.plotly_chart(plotting_graph3(df1, df2, option_piloto1, option_piloto2))
        #         except Exception as e:
        #             col1.error(f"Erro ao carregar telemetria: Piloto não concluiu a volta")

with col2:
    display_next_race_sessions(col2)

    fig = plot_circuit()
    st.pyplot(fig)

import streamlit as st
import fastf1 as ff1
import pandas as pd
import plotly.graph_objects as go

@st.cache_data
def get_circuits(year):
        if year:
            schedule = ff1.get_event_schedule(year)["EventName"].unique()
            return list(schedule)
        return []
    
@st.cache_data(show_spinner=False)
def get_pilots(year, circuit):
    if year and circuit:
        race = ff1.get_session(year, circuit, "R")
        race.load()
        drivers = race._drivers_from_f1_api()
        drivers_df = pd.DataFrame(drivers[["Abbreviation", "FullName"]])
        laps = list(range(1, race._total_laps + 1))
        return drivers_df, race, laps
    return pd.DataFrame(columns=["Abbreviation", "FullName"]), None

def speed_graph(df1, df2, option_driver1, option_driver2):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df1['Distance'], y=df1['Speed'], mode='lines', name=option_driver1))
    fig.add_trace(go.Scatter(x=df2['Distance'], y=df2['Speed'], mode='lines', name=option_driver2))
    fig.update_layout(title='Distance x Speed', xaxis_title='Distance (m)', yaxis_title='Speed (km/h)', template='plotly_dark')
    return fig

def throttle_graph(df1, df2, option_driver1, option_driver2):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df1['Distance'], y=df1['Throttle'], mode='lines', name=option_driver1))
    fig.add_trace(go.Scatter(x=df2['Distance'], y=df2['Throttle'], mode='lines', name=option_driver2))
    fig.update_layout(title='Distance x Throttle', xaxis_title='Distance (m)', yaxis_title='Throttle', template='plotly_dark')
    return fig

def gear_graph(df1, df2, option_driver1, option_driver2):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df1['Distance'], y=df1['nGear'], mode='lines', name=option_driver1))
    fig.add_trace(go.Scatter(x=df2['Distance'], y=df2['nGear'], mode='lines', name=option_driver2))
    fig.update_layout(title='Distance x Gear', xaxis_title='Distance (m)', yaxis_title='Gear', template='plotly_dark')
    return fig

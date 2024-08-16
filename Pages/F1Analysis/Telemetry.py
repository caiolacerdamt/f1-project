import streamlit as st
import fastf1 as ff1
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime as dt

@st.cache_data
def get_circuits(): 
        events_schedule = ff1.get_event_schedule(dt.now().year)
        today = pd.Timestamp.now()
        finished_events = events_schedule[events_schedule["EventDate"] <= today]
        return list(finished_events["EventName"][1:])
    
@st.cache_data(show_spinner=False)
def get_circuit_data(circuit):
    race = ff1.get_session(dt.now().year, circuit, "R")
    race.load(weather=False, messages=False)
    drivers = race._drivers_from_f1_api()
    drivers_df = pd.DataFrame(drivers[["Abbreviation", "FullName"]])
    laps = list(range(1, race._total_laps + 1))
    return drivers_df, laps, race

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

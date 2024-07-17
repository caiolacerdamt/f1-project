import streamlit as st
import fastf1 as ff1
import nbimporter
import main

# df_telemetry = main.ham_tel()
# df_ver = main.ver_tel()
# my_chart = st.line_chart(df_telemetry, x="Distance", y="Speed")
# my_chart.add_rows(df_ver, x="Distance", y="Speed")

col1_ano, col2_circuito = st.columns(2)

anos = list(range(2018, 2025))

with col1_ano:
    option_ano = st.selectbox(
        "Escolha o ano",
        anos,
        index=None,
        key="selectbox_ano"
    )

def get_circuits(year):
    if year is not None:
        schedule = ff1.get_event_schedule(year)["EventName"].unique()
        event_name = [event for event in schedule]
        return event_name
    else:
        return []

if option_ano is not None:
    circuits = get_circuits(option_ano)
    with col2_circuito:
        option_circuito = st.selectbox(
            "Circuito",
            circuits,
            index=None,
            key="selectbox_circuito",
            placeholder="Escolha um circuito",
        )

def get_pilots(year, circuit):
    if (year is not None) and (circuit is not None):
        race = ff1.get_session(year, circuit, "R")
        race.load()
        drivers = race._drivers_from_f1_api()['FullName'].unique()
        drivers_name = [driver for driver in drivers]
        return drivers_name, race
    else: 
        return [], None

pilotos = None
race = None

if (option_ano is not None) and (option_circuito is not None): 
    pilotos, race = get_pilots(option_ano, option_circuito)
    col1_piloto, col2_piloto = st.columns(2)
    with col1_piloto:
        option_piloto1 = st.selectbox(
            "Piloto 1",
            pilotos,
            index=None,
            key="selextbox_piloto1",
            placeholder="Escolha um piloto"
        )

    with col2_piloto:
        option_piloto2 = st.selectbox(
            "Piloto 2",
            pilotos,
            index=None,
            key="selextbox_piloto2",
            placeholder="Escolha um piloto"
        )    

def get_numbers_of_laps(race):
    if race is not None:
        return list(range(1, race._total_laps + 1))
    else:
        return []

if race is not None:
    laps = get_numbers_of_laps(race)
else:
    laps = None

custom_css = """
<style>
    .stButton button {
        border: none !important; 
        background-color: #4CAF50; 
        color: white; 
        text-align: center;
        font-size: 16px; 
        padding: 10px;
        margin: 27.99px; 
        cursor: pointer;
        border-radius: 8px;
        height: 40px;
        width: 200px;
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

if laps:
    col1_lap, col2_button = st.columns([2, 1])

    with col1_lap:
        option_lap = st.selectbox(
            "Volta",
            laps,
            index=None,
            key="selectbox_laps",
            placeholder="Escolha a volta"
        )
    
    with col2_button:
            if st.button(label='Mostrar Gráfico de Telemetria'):
                st.write(f"Ação executada com os seguintes valores:")
                st.write(f"Ano: {option_ano}")
                st.write(f"Circuito: {option_circuito}")
                st.write(f"Primeiro piloto: {option_piloto1}")
                st.write(f"Segundo piloto: {option_piloto2}")

ver_data, ham_data = main.plotar_grafico()

st.line_chart(ham_data.set_index("Distance"))
# st.line_chart(ver_data.set_index("Distance"))
import streamlit as st
import Pages.F1Analysis.Telemetry as Telemetry
import Pages.F1Analysis.Season as Season
from datetime import datetime as dt

st.set_page_config(layout="wide")

menu = st.sidebar.selectbox("Menu", ("Telemetry", "Season Info"))

year = dt.now().year

if menu == "Telemetry":
    st.title(f"Telemetry Analysis - {year}")

    option_circuit = None
    option_driver1 = None
    option_driver2 = None
    option_laps = None

    #option_year = st.selectbox("Choose the year", years, index=None)
    circuits = Telemetry.get_circuits()
    option_circuit = st.selectbox("Circuit", circuits, index=None, placeholder="Choose a circuit")

    if option_circuit is not None:
        try:
            with st.spinner("Loading data - This might take a while"):
                drivers, laps, race = Telemetry.get_circuit_data(option_circuit)
                option_driver1 = st.selectbox("Driver 1", drivers["FullName"].tolist(), index=None, placeholder="Choose a driver")
                option_driver2 = st.selectbox("Driver 2", drivers["FullName"].tolist(), index=None, placeholder="Choose a driver")
                option_laps = st.selectbox("Lap", laps, index=None, placeholder="Choose a lap")
        except Exception as e:
            st.error("Race not finished yet")

    if option_driver1 is not None and option_driver2 is not None and option_laps is not None:
        show_graphs = st.button("Show graphs")
        
        if show_graphs:
            abbreviation_driver1 = drivers.loc[drivers["FullName"] == option_driver1, "Abbreviation"].iloc[0]
            abbreviation_driver2 = drivers.loc[drivers["FullName"] == option_driver2, "Abbreviation"].iloc[0]
            telemetry_driver1 = race.laps.pick_driver(abbreviation_driver1).pick_lap(option_laps).get_car_data().add_distance()
            telemetry_driver2 = race.laps.pick_driver(abbreviation_driver2).pick_lap(option_laps).get_car_data().add_distance()

            st.subheader(f"Telemetry Graphs {option_driver1} x {option_driver2} - {option_circuit} {year} - Lap: {option_laps}")
            st.plotly_chart(Telemetry.speed_graph(telemetry_driver1, telemetry_driver2, option_driver1, option_driver2))
            st.plotly_chart(Telemetry.throttle_graph(telemetry_driver1, telemetry_driver2, option_driver1, option_driver2))
            st.plotly_chart(Telemetry.gear_graph(telemetry_driver1, telemetry_driver2, option_driver1, option_driver2))

if menu == "Season Info":
    st.markdown(f"""
                <h1 style="text-align: center;">
                    Season - {year}
                </h1>
                """, unsafe_allow_html=True)
    container1, container2 = st.columns([1,1.5])
    with container1:
        st.markdown(f"""
                    <h3 style="text-align: center;">Drivers Standings</h3>
                    """, unsafe_allow_html=True)
        driver_standings = Season.get_driver_standings()
        html_standing = driver_standings.style \
            .set_properties(**{
                'border': 'none',
                'padding': '6px 12px',
            }) \
            .set_table_styles({
                'table': [{
                    'selector': 'table',
                    'props': 'width: 80%; margin: 0 auto;'
                }]
            }) \
            .hide(axis='index').to_html()
        st.markdown(html_standing, unsafe_allow_html=True)
    with container2:
        col1, col2 = st.columns([1, 1])
        with col1:
            next_race = Season.display_next_race_sessions()

        with col2:
            names, probs = Season.load_predictions()
            st.markdown(f"""
                <h3 style="text-align: center;">Chance to win</h3>
            """, unsafe_allow_html=True)
            for name, prob in zip(names, probs):
                st.markdown(f"""
                    <p style="text-align:center;">{name} - {prob:.2f}%</p>
                """, unsafe_allow_html=True)

        circuit_image = Season.plot_circuit()
        st.image(circuit_image)


     

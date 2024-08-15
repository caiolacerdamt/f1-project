import streamlit as st
import Pages.F1Analysis.Telemetry as Telemetry
import Pages.F1Analysis.Season as Season

st.set_page_config(layout="wide")

menu = st.sidebar.selectbox("Menu", ("Telemetry", "Season Info"))

if menu == "Telemetry":
    st.title("Telemetry Analysis")

    years = list(range(2018, 2025))
    option_year = None
    option_circuit = None
    option_driver1 = None
    option_driver2 = None
    option_laps = None

    option_year = st.selectbox("Choose the year", years, index=None)

    if option_year is not None:
        with st.spinner("Loading Circuits"):
            circuits = Telemetry.get_circuits(option_year)
            option_circuit = st.selectbox("Circuit", circuits, index=None, placeholder="Choose a circuit")

    if option_year is not None and option_circuit is not None:
        try:
            with st.spinner("Loading data - This might take a while"):
                drivers, race, laps = Telemetry.get_pilots(option_year, option_circuit)
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

            st.subheader(f"Telemetry Graphs {option_driver1} x {option_driver2} - {option_circuit} {option_year} - Lap: {option_laps}")
            st.plotly_chart(Telemetry.speed_graph(telemetry_driver1, telemetry_driver2, option_driver1, option_driver2))
            st.plotly_chart(Telemetry.throttle_graph(telemetry_driver1, telemetry_driver2, option_driver1, option_driver2))
            st.plotly_chart(Telemetry.gear_graph(telemetry_driver1, telemetry_driver2, option_driver1, option_driver2))

if menu == "Season Infos":
    next_race = 'Next Race Info'
    st.markdown(f"""
        <div style='text-align:center; font-size:24px; font-weight:bold;'>{next_race}</div>
        """, unsafe_allow_html=True)
    Season.display_next_race_sessions()
    Season.plot_circuit()
    names, probs = Season.load_predictions()
    st.write("Top 3 Probabilities to Winner")
    for name, prob in zip(names, probs):
        st.write(f"{name} - {prob:.2f}%")
     

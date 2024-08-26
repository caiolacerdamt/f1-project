import streamlit as st
import Pages.F1Analysis.Telemetry as Telemetry
import Pages.F1Analysis.NextRace as NextRace
import Pages.F1Analysis.Standings as Standings
from datetime import datetime as dt

st.set_page_config(layout="wide")

menu = st.sidebar.selectbox("Menu", ("Telemetry", "Next Race Info", "Standings"))

year = dt.now().year

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');
    h1, h2, h3, h4, h5, th, td, p {
        font-family: 'Kanit', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

if menu == "Telemetry":
    st.title(f"Telemetry Analysis - {year}")

    option_circuit = None
    option_driver1 = None
    option_driver2 = None
    option_laps = None

    with st.spinner("Loading Circuits"):
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

if menu == "Next Race Info":
    
    st.markdown(f"""
                <div style="text-align: center;">
                    <p style="font-size: 32px; font-weight: bold;">Next Round
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown(f"<br><br>", unsafe_allow_html=True)

    circuit_info, date_events, probabilities_table = st.columns(3)
    
    with circuit_info:
        with st.spinner("Loading Next Circuit Info..."):
            country_name, country_flag_url, circuit_url = NextRace.get_flag_and_circuit_images()

            st.markdown(f"""
                    <div style="display: flex; justify-content:center; align-items: center;">
                        <p style="font-size: 28px;">{country_name}  -  <img src="{country_flag_url}" alt="Country Flag" style="width: 60px;"/>
                    """,unsafe_allow_html=True)
        
            st.markdown(f"""
                    <div style="text-align: center;">
                    <img src="{circuit_url}" alt="Circuit Flag" style="width: 300px;"/>
                    <figcaption> {country_name} Circuit
                    """, unsafe_allow_html=True)
    
    with date_events:
        with st.spinner("Loading Dates..."):
            next_race_info = NextRace.get_next_race_times()

            st.markdown(f"""
                    <p style="font-size: 28px; text-align: center;"> {next_race_info.Date.iloc[0]} to {next_race_info.Date.iloc[-1]}
                    """, unsafe_allow_html=True)
            
            html_standing2 = next_race_info.style \
                .set_properties(**{
                    'border': 'none',
                    'padding': '6px 12px',
                }) \
                .set_table_styles({
                    'table': [{
                        'selector': 'table',
                        'props': 'width: 100%; margin: 0 auto;'
                    }]
                }) \
                .hide(axis='index').to_html()
        

            st.markdown(f"""
                    <div style="display: flex; justify-content: center;"> {html_standing2}
                    """, unsafe_allow_html=True)
            st.markdown(f"""
                        <p style="text-align: center; font-weight: 200;"> ( Track Times )
                    """, unsafe_allow_html=True)
    st.markdown(f"<br><br>", unsafe_allow_html=True)
    st.warning(f"""The predictions are based on available data and algorithms, and are not guaranteed to be 100% accurate. 
               Outcomes may vary due to unforeseen factors and changes in race conditions.""")
        
    with probabilities_table:
        with st.spinner("Loading Predictions..."):
            predictions = NextRace.load_predictions()

            st.markdown(f"""
                          <p style="font-size: 28px; text-align: center;"> Chance to win
                        """
                    , unsafe_allow_html=True)
        
            html_predictions = predictions.style \
                .set_properties(**{
                    'border': 'none',
                    'padding': '6px 12px',
                }) \
                .set_table_styles({
                    'table': [{
                        'selector': 'table',
                        'props': 'width: 100%; margin: 0 auto;'
                }]
            }) \
        .hide(axis='index').to_html()

            st.markdown(f"""
                    <div style="display: flex; justify-content: center;"> {html_predictions}
                    """, unsafe_allow_html=True)
            st.markdown(f"""
                    <p style="text-align: center; font-weight: 200;"> The values may be changed.
                    """, unsafe_allow_html=True)

if menu == 'Standings':

    st.markdown(f"""
                <p style="font-size: 32px; font-weight: bold; text-align: center;">
                    Standings so far
                """, unsafe_allow_html=True)

    with st.spinner("Loading Driver Standings..."):
        drivers, teams = st.columns(2)
        
        with drivers:

            st.markdown(f"""
                        <p style="text-align: center; font-size: 28px;"> Drivers Standings
                        """, unsafe_allow_html=True)

            driver_standings = Standings.get_driver_standings()

            html_driver_standing = driver_standings.style \
            .set_properties(**{
                'border': 'none',
                'padding': '6px 12px',
            }) \
            .set_table_styles({
                'table': [{
                    'selector': 'table',
                    'props': 'width: 90%; margin: 0 auto;'
                }]
            }) \
            .hide(axis='index').to_html()

            st.markdown(f"""
                <div style="display: flex; justify-content: center; align-items: center;">
                    {html_driver_standing}
                 """, unsafe_allow_html=True)
                
        with teams:

            st.markdown(f"""
                        <p style="text-align: center; font-size: 28px;"> Constructors Standings
                        """, unsafe_allow_html=True)

            constructor_standings = Standings.get_contructor_standings()
            html_constructor_standing = constructor_standings.style \
                .set_properties(**{
                    'border': 'none',
                    'padding': '6px 12px',
                }) \
                .set_table_styles({
                    'table': [{
                        'selector': 'table',
                        'props': 'width: 90%; margin: 0 auto;'
                    }]
                }) \
                .hide(axis='index').to_html()
        
            st.markdown(f"""
                <div style="display: flex; justify-content: center; align-items: center;">
                    {html_constructor_standing}
                """, unsafe_allow_html=True)



     

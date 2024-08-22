import streamlit as st
import Pages.F1Analysis.Telemetry as Telemetry
import Pages.F1Analysis.Season as Season
from datetime import datetime as dt

st.set_page_config(layout="wide")

menu = st.sidebar.selectbox("Menu", ("Telemetry", "Season Info"))

year = dt.now().year

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');
    h1, h2, h3, h4, h5, p, th, td {
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
                <h1 style="text-align: center; margin-bottom: 50px;">
                    Season - {year}
                </h1>
                """, unsafe_allow_html=True)


    st.markdown(f"""
                <h3 style="text-align: center; margin-top: 50px;">Drivers Standings</h3>
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
                    'props': 'width: 90%; margin: 0 auto;'
                }]
            }) \
            .hide(axis='index').to_html()

    st.markdown(f"""
                <div style="display: flex; justify-content: center; align-items: center;">
                    {html_standing}
                """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.markdown(f"""
                <div style="text-align: center; margin-top: 50px;">
                    <h3>Next Race</h3>
                </div>
                """, unsafe_allow_html=True)

    img1, img2 = Season.get_flag_and_circuit_images()

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.image(img1, width=50)
        st.markdown(f"""
                    <div style="text-align: center;">
                        <h4>Holanda</h4>
                    </div>
                    """, unsafe_allow_html=True)
        next_race_info = Season.create_event_dataframe()
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
        st.markdown(html_standing2, unsafe_allow_html=True)
    
    with col2:
        st.image(img2, width=300)

        predictions = Season.load_predictions()
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

    st.markdown(html_predictions, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)



     

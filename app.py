import streamlit as st
import nbimporter
import main

# df_telemetry = main.ham_tel()
# df_ver = main.ver_tel()
# my_chart = st.line_chart(df_telemetry, x="Distance", y="Speed")
# my_chart.add_rows(df_ver, x="Distance", y="Speed")

col1_ano, col2_circuito = st.columns(2)

circuitos = ("Silverstone", "Interlagos", "Speilberg")
anos = ("2020", "2021", "2022", "2023")

with col1_ano:
    option_ano = st.selectbox(
        "Escolha o ano",
        anos,
        index=None,
        key="selectbox_ano"
    )

with col2_circuito:
    option_circuito = st.selectbox(
        "Escolha o circuito",
        circuitos,
        index=None,
        key="selectbox_circuito"
    )

pilotos = ("Leclerc", "Hamilton", "Verstappen")

col1_piloto, col2_piloto = st.columns(2)

with col1_piloto:
    option_piloto1 = st.selectbox(
        "Escolha o primeiro piloto",
        pilotos,
        index=None,
        key="selextbox_piloto1"
    )

with col2_piloto:
    option_piloto2 = st.selectbox(
        "Escolha o segundo piloto",
        pilotos,
        index=None,
        key="selextbox_piloto2"
    )

with st.form(key='my_form'):
    if st.form_submit_button(label='Executar Ação'):
        # Aqui você pode chamar sua função com os valores selecionados
        st.write(f"Ação executada com os seguintes valores:")
        st.write(f"Ano: {option_ano}")
        st.write(f"Circuito: {option_circuito}")
        st.write(f"Primeiro piloto: {option_piloto1}")
        st.write(f"Segundo piloto: {option_piloto2}")

ver_data, ham_data = main.plotar_grafico()

st.line_chart(ham_data.set_index("Distance"))
# st.line_chart(ver_data.set_index("Distance"))
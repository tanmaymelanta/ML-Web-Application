import streamlit as st
import pandas as pd
import pydeck as pdk

mp_style_dict = {'Light mode': 'mapbox://styles/mapbox/light-v9', 
                 'Dark mode': 'mapbox://styles/mapbox/dark-v9', 
                 'Street map': 'mapbox://styles/mapbox/streets-v11', 
                 'Satellite': 'mapbox://styles/mapbox/satellite-v9', 
                 'Satellite streets': 'mapbox://styles/mapbox/satellite-streets-v11'}

@st.cache_resource
def load_data():
    data = pd.read_csv(r"C:\Users\Project\Ship Data.csv")
    data['UTC Timestamp'] = pd.to_datetime(data['UTC Timestamp'])
    return data

@st.cache_resource
def load_ship_data(df, ship_name, frequency):
    filtered_data = df[df['Ship Name'] == ship_name]
    filtered_data.set_index('UTC Timestamp', inplace=True)
    resampled_data = filtered_data[['Latitude', 'Longitude']].resample(frequency).mean()
    resampled_data.reset_index(inplace=True)
    resampled_data = resampled_data.dropna()
    return resampled_data

def plot_vessel_trade(data, title, map_style):
    st.markdown(title)
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=data,
        get_position='[Longitude, Latitude]',
        get_radius=100,
        radius_scale=10,
        radius_min_pixels=2,
        radius_max_pixels=20,
        get_color=[255, 0, 0],
        pickable=True
    )
    view_state = pdk.ViewState(
        latitude=0,
        longitude=0,
        zoom=0,
        pitch=0
    )
    r = pdk.Deck(layers=[layer], initial_view_state=view_state, map_style=map_style)
    st.pydeck_chart(r)

# Main function to run the app
def main():
    st.title("Ship Trade Pattern")
    data = load_data()
    st.sidebar.subheader("Choose a Ship")
    Ship = st.sidebar.selectbox('Select a Vessel', data['Ship Name'].unique())
    mp_style = st.sidebar.selectbox('Select Map Style', ('Satellite streets', 'Light mode', 'Dark mode', 'Street map', 'Satellite'))
    col1, col2 = st.sidebar.columns(2)
    with col2:
        freq = st.selectbox("", ('daily', 'hourly'), key='freq_type')
        if freq == 'daily':
            with col1:
                freq_num = st.selectbox("Select Data Frequency", 1, key='freq_num')
        elif freq == 'hourly':
            with col1:
                freq_num = st.selectbox("Select Data Frequency", (1, 2, 3, 4, 6, 8, 12, 24), key='freq_num')
    if freq == 'hourly':
        frequency = str(freq_num)+'h'
    elif freq == 'daily':
        frequency = str(freq_num)+'D'
    df = load_ship_data(df=data, ship_name=Ship, frequency=frequency)
    map_style = mp_style_dict[mp_style]
    df_23 = df[df['UTC Timestamp'].dt.year == 2023]
    df_22 = df[df['UTC Timestamp'].dt.year == 2022]

    if not df_23.empty:
        plot_vessel_trade(df_23, f"Ship Trade Pattern for {Ship} in 2023", map_style)
    if not df_22.empty:
        plot_vessel_trade(df_22, f"Ship Trade Pattern for {Ship} in 2022", map_style)
    
    options = [("Show Ship Data", df)]
    for opt, data in options:
        if st.sidebar.checkbox(opt, False):
            st.dataframe(data, hide_index=True)

if __name__ == '__main__':
    main()

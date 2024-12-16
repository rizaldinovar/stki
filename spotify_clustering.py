import pandas as pd # type: ignore
import requests # type: ignore
import streamlit as st # type: ignore
import plotly.express as px # type: ignore
from sklearn import preprocessing # type: ignore
from sklearn.decomposition import PCA # type: ignore
from sklearn.cluster import KMeans # type: ignore

# Fungsi untuk mengambil token (Anda dapat menggunakan token yang sudah didapatkan)
def getToken():
    # Gunakan token yang sudah diberikan
    return 'BQDzB_PZCnSkwszkp8l2RDN5TiTc8hdcw_ZMJ5HPkYxXTDQ68ToSIOkqlzhyeeLb6wBBBR1_GipTDJSmEabtQhG2tIapUfbqah5tt1wMNruDvnYT1fA'

# Fungsi untuk mengambil track dari playlist
def getPlaylistItems(token, playlist_id):
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        json_result = response.json()
        track_data = []
        
        # Ambil data track (Nama track dan Track ID)
        for item in json_result['items']:
            track_name = item['track']['name']
            track_id = item['track']['id']
            artist_name = item['track']['artists'][0]['name']  # Ambil nama artist pertama
            track_data.append([artist_name, track_name, track_id])
        
        # Mengonversi track data menjadi DataFrame untuk analisis selanjutnya
        track_df = pd.DataFrame(track_data, columns=['artist', 'name', 'track_id'])
        st.write("## Track Data from Playlist")
        st.write(track_df)

        return track_df
    else:
        st.write(f"Failed to retrieve playlist tracks: {response.status_code}")
        return None

# Proses data untuk clustering dan visualisasi
def dataProcessing(track_df):
    st.write("## Preprocessing Result")  # streamlit widget

    # Check if 'mode' exists before dropping it
    if 'mode' in track_df.columns:
        track_df = track_df.drop(['mode'], axis=1)

    track_df['artist'] = track_df['artist'].map(lambda x: str(x)[2:-1])
    track_df['name'] = track_df['name'].map(lambda x: str(x)[2:-1])
    st.write("### Data to be deleted:")
    track_df = track_df[track_df['name'] != '']

    # Check if the columns exist before dropping
    drop_columns = ['artist', 'name', 'year', 'popularity', 'key', 'duration_ms']
    columns_to_drop = [col for col in drop_columns if col in track_df.columns]

    track_df2 = track_df.copy()
    track_df2 = track_df2.drop(columns=columns_to_drop, axis=1)

    st.write("## Normalization Result")  # streamlit widget

    # Select only numeric columns for scaling
    numeric_columns = track_df2.select_dtypes(include=['float64', 'int64']).columns
    if len(numeric_columns) == 0:
        st.error("No numeric columns available for scaling!")
        return

    track_df2_numeric = track_df2[numeric_columns]

    # Handle non-numeric values or NaN before scaling
    track_df2_numeric = track_df2_numeric.apply(pd.to_numeric, errors='coerce')

    # Check if there are any NaN values after coercion
    if track_df2_numeric.isnull().sum().sum() > 0:
        st.error("There are NaN values in the numeric columns after conversion. Please clean the data.")
        return

    # Apply MinMaxScaler only to numeric data
    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(track_df2_numeric)
    track_df2[numeric_columns] = x_scaled

    st.write("## Dimensionality Reduction with PCA")  # streamlit widget
    pca = PCA(n_components=2)
    pca.fit(track_df2_numeric)
    pca_data = pca.transform(track_df2_numeric)
    pca_df = pd.DataFrame(data=pca_data, columns=['x', 'y'])
    fig = px.scatter(pca_df, x='x', y='y', title='PCA')
    st.plotly_chart(fig)  # output plotly chart using streamlit

    st.write("## Clustering with K-Means")  # streamlit widget
    track_df2 = list(zip(pca_df['x'], pca_df['y']))
    kmeans = KMeans(n_init=10, max_iter=1000).fit(track_df2)
    fig = px.scatter(pca_df, x='x', y='y', color=kmeans.labels_,
                     color_continuous_scale='rainbow', hover_data=[track_df.artist, track_df.name])
    st.plotly_chart(fig)  # output plotly chart using streamlit

    st.write("Enjoy!")

# streamlit widgets
st.write("# Spotify Playlist Clustering")
client_id = st.text_input("Enter Client ID")
client_secret = st.text_input("Enter Client Secret")
playlistId = st.text_input("Enter Playlist ID")

# streamlit widgets
if st.button('Create Dataset!'):
    token = getToken()
    track_df = getPlaylistItems(token, playlistId)
    if track_df is not None:
        dataProcessing(track_df)
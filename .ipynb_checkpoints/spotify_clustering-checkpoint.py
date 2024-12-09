import streamlit as st # type: ignore
import pandas as pd # type: ignore
import numpy as np # type: ignore
from sklearn.cluster import KMeans # type: ignore
from sklearn.decomposition import PCA # type: ignore
import plotly.express as px # type: ignore
import base64
from requests import post, get # type: ignore
import json
import csv
from sklearn import preprocessing # type: ignore

client_id = '112da7a2d76143b3a123502f7e78240d' ##ganti variabel dengan client_id milik anda
client_secret = 'f796472edc0a4fe281171cf4be64d809' ##ganti variabel dengan client_secret milik anda
playlistId = '1dtCMTYzAOzwKXqklxPJNS'

## 37i9dQZF1DXbrUpGvoi3TS - 1(similar sad songs)
## 1dtCMTYzAOzwKXqklxPJNS - 2(old songs, rock, rap)
## 0IN7IWKmIfwlEysGyWUuRg - 3(mix of modern electronic, pop, and rock)

dataset = []
dataset2 = []
dataset3 = []

def getToken():
    # gabungkan client_id dan client_secret
    auth_string = client_id + ':' + client_secret

    # encode ke base64
    auth_b64 = base64.b64encode(auth_string.encode('utf-8'))

    # url untuk mengambil token
    url = 'https://accounts.spotify.com/api/token'

    # header untuk mengambil token - sesuai dengan guide dari spotify
    headers = {
        'Authorization': 'Basic ' + auth_b64.decode('utf-8'),
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # data untuk mengambil token - sesuai dengan guide dari spotify
    data = {'grant_type': 'client_credentials'}

    # kirim request POST ke spotify
    result = post(url, headers=headers, data=data)

    # parse response ke json
    json_result = json.loads(result.content)
    token = json_result['access_token']

    # ambil token untuk akses API
    return token

## panggil fungsi getToken() dibawah ini
## pengambilan token untuk otorisasi API
def getAuthHeader(token):
    return {'Authorization': 'Bearer ' + token}

## pengambilan audio features dari track (lagu)
def getAudioFeatures(token, trackId):
    # endpoint untuk akses playlist
    url = f'https://api.spotify.com/v1/audio-features/{trackId}'
    # ambil token untuk otorisasi, gunakan sebagai header
    headers = getAuthHeader(token)
    result = get(url, headers=headers)  # kirim request GET ke spotify
    json_result = json.loads(result.content)  # parse response ke json

    # ambil data yang diperlukan dari response
    audio_features_temp = [
        json_result['danceability'],
        json_result['energy'],
        json_result['key'],
        json_result['loudness'],
        json_result['mode'],
        json_result['speechiness'],
        json_result['acousticness'],
        json_result['instrumentalness'],
        json_result['liveness'],
        json_result['valence'],
        json_result['tempo'],
    ]
    dataset2.append(audio_features_temp)

# pengambilan track (lagu) dari playlist
def getPlaylistItems(token, playlistId):
    # endpoint untuk akses playlist
    url = f'https://api.spotify.com/v1/playlists/{playlistId}/tracks'
    limit = '&limit=100'  # batas maksimal track yang diambil
    market = '?market=ID'  # negara yang tempat aplikasi diakses
    # format data dari track yang diambil
    fields = '&fields=items%28track%28id%2Cname%2Cartists%2Cpopularity%2C+duration_ms%2C+album%28release_date%29%29%29'
    url = url+market+fields+limit  # gabungkan semua parameter
    # ambil token untuk otorisasi, gunakan sebagai header
    headers = getAuthHeader(token)
    result = get(url, headers=headers)  # kirim request GET ke spotify
    json_result = json.loads(result.content)  # parse response ke json
    # print(json_result)

    # ambil data yang diperlukan dari response
    for i in range(len(json_result['items'])):
        playlist_items_temp = []
        playlist_items_temp.append(json_result['items'][i]['track']['id'])
        playlist_items_temp.append(
            json_result['items'][i]['track']['name'].encode('utf-8'))
        playlist_items_temp.append(
            json_result['items'][i]['track']['artists'][0]['name'].encode('utf-8'))
        playlist_items_temp.append(
            json_result['items'][i]['track']['popularity'])
        playlist_items_temp.append(
            json_result['items'][i]['track']['duration_ms'])
        playlist_items_temp.append(
            int(json_result['items'][i]['track']['album']['release_date'][0:4]))
        dataset.append(playlist_items_temp)

    # ambil audio features dari semua track di dalam playlist
    for i in range(len(dataset)):
        getAudioFeatures(token, dataset[i][0])

    # gabungkan dataset dan dataset2
    for i in range(len(dataset)):
        dataset3.append(dataset[i]+dataset2[i])

    print(dataset3)
    # convert dataset3 into csv
    with open('dataset.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["id", "name", "artist", "popularity", "duration_ms", "year", "danceability", "energy", "key", "loudness", "mode",
                         "speechiness", "acousticness", "instrumentalness", "liveness", "valence", "tempo"])
        writer.writerows(dataset3)

token = getToken()
print('access token : '+token)
getPlaylistItems(token, playlistId)

import pandas as pd # type: ignore
import numpy as np # type: ignore

from sklearn.cluster import KMeans # type: ignore
from sklearn.decomposition import PCA # type: ignore

import plotly.express as px  # type: ignore

## muat dataset
data = pd.read_csv('dataset.csv')
data.head()

## Hapus karakter yang tidak perlu pada kolom artist dan name
data['artist'] = data['artist'].map(lambda x: str(x)[2:-1])
data['name'] = data['name'].map(lambda x: str(x)[2:-1])

data.head()

##delete empty string in name column
data = data[data['name'] != '']

##reset index
data = data.reset_index(drop=True)
data.head()

## drop name artist and year column
data2 = data.copy()
data2 = data2.drop(['artist', 'name', 'year', 'popularity', 'key','duration_ms', 'mode', 'id'], axis=1)

data2.head()

from sklearn import preprocessing # type: ignore

## normalize all data to 0 and 1
x = data2.values ##returns a numpy array
min_max_scaler = preprocessing.MinMaxScaler()
x_scaled = min_max_scaler.fit_transform(x)
data2 = pd.DataFrame(x_scaled)

## convert to dataframe
data2.columns = ['acousticness','danceability','energy','instrumentalness','loudness', 'liveness', 'speechiness', 'tempo','valence']

## data2.head()
data2.describe()

## Lakukan PCA untuk mengurangi jumlah fitur menjadi 2 fitur saja
pca = PCA(n_components=2)
pca.fit(data2)
pca_data = pca.transform(data2)

## buat dataframe dari hasil pca
pca_df = pd.DataFrame(data=pca_data, columns=['x', 'y'])
pca_df.head()

## plot pca_df using plotly
fig = px.scatter(pca_df, x='x', y='y', title='PCA')
fig.show()

## rubah bentuk data ke list 
data2 = list(zip(pca_df['x'], pca_df['y']))

## fit kmeans model
kmeans = KMeans(n_init=10, max_iter=1000).fit(data2)

## make scatter plot using plotly
fig = px.scatter(pca_df, x='x', y='y', color=kmeans.labels_, color_continuous_scale='rainbow', hover_data=[data.artist, data.name])
fig.show()

def dataProcessing():
    data = pd.read_csv('dataset.csv')
    data
    st.write("## Preprocessing Result")  # streamlit widget

    data = data[['artist', 'name', 'year', 'popularity', 'key', 'mode', 'duration_ms', 'acousticness',
                'danceability', 'energy', 'instrumentalness', 'loudness', 'liveness', 'speechiness', 'tempo', 'valence']]
    data = data.drop(['mode'], axis=1)
    data['artist'] = data['artist'].map(lambda x: str(x)[2:-1])
    data['name'] = data['name'].map(lambda x: str(x)[2:-1])
    st.write("### Data to be deleted:")
    data[data['name'] == '']
    data = data[data['name'] != '']

    st.write("## Normalization Result")  # streamlit widget
    data2 = data.copy()
    data2 = data2.drop(
        ['artist', 'name', 'year', 'popularity', 'key', 'duration_ms'], axis=1)
    x = data2.values
    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(x)
    data2 = pd.DataFrame(x_scaled)
    data2.columns = ['acousticness', 'danceability', 'energy', 'instrumentalness',
                     'loudness', 'liveness', 'speechiness', 'tempo', 'valence']
    data2

    st.write("## Dimensionality Reduction with PCA")  # streamlit widget
    pca = PCA(n_components=2)
    pca.fit(data2)
    pca_data = pca.transform(data2)
    pca_df = pd.DataFrame(data=pca_data, columns=['x', 'y'])
    fig = px.scatter(pca_df, x='x', y='y', title='PCA')
    st.plotly_chart(fig)  # output plotly chart using streamlit

    st.write("## Clustering with K-Means")  # streamlit widget
    data2 = list(zip(pca_df['x'], pca_df['y']))
    kmeans = KMeans(n_init=10, max_iter=1000).fit(data2)
    fig = px.scatter(pca_df, x='x', y='y', color=kmeans.labels_,
                     color_continuous_scale='rainbow', hover_data=[data.artist, data.name])
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
    getPlaylistItems(token, playlistId)
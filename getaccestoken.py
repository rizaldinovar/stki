import streamlit as st # type: ignore
import base64
from requests import post # type: ignore
import json

# Masukkan Client ID dan Client Secret Anda
client_id = '112da7a2d76143b3a123502f7e78240d'  # Ganti dengan Client ID Anda
client_secret = 'f796472edc0a4fe281171cf4be64d809'  # Ganti dengan Client Secret Anda

# Fungsi untuk mendapatkan Access Token
def get_token(client_id, client_secret):
    # Encode client_id dan client_secret dalam format Base64
    auth_string = f"{client_id}:{client_secret}"
    auth_b64 = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

    # URL untuk mengambil token dari Spotify API
    url = 'https://accounts.spotify.com/api/token'

    # Header untuk autentikasi
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Data untuk permintaan token
    data = {'grant_type': 'client_credentials'}

    # Kirim permintaan POST untuk mendapatkan token
    response = post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        st.error(f"Failed to get access token: {response.status_code} - {response.json()}")
        return None

# Streamlit UI
def main():
    st.title("Spotify API Token Generator")

    # Tombol untuk menghasilkan Access Token
    if st.button("Generate Access Token"):
        token = get_token(client_id, client_secret)
        if token:
            st.success("Access Token generated successfully!")
            st.code(f"Access Token: '{token}'", language='python')  # Menampilkan token

# Jalankan aplikasi
if __name__ == "__main__":
    main()

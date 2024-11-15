# Import semua modul yang dibutuhkan
import time
import os
import joblib
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# Memuat variabel-variabel dari file .env
load_dotenv()

# Mendapatkan API Key dari file .env, yang akan digunakan untuk mengakses API Gemini
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# Konfigurasi API Gemini menggunakan API Key
genai.configure(api_key=GOOGLE_API_KEY)

# Membuat ID unik untuk setiap chat baru
new_chat_id = f'{time.time()}'
MODEL_ROLE = 'ai'
AI_AVATAR_ICON = '🤖'

# Membuat folder "data" jika belum ada. Folder ini digunakan untuk menyimpan chat lama.
if not os.path.exists('data/'):
    os.mkdir('data/')

# Memuat daftar chat lama (jika ada). Kita simpan daftar ini di file `data/past_chats_list`
try:
    past_chats = joblib.load('data/past_chats_list')
except:
    past_chats = {}

# Sidebar untuk memilih chat lama
with st.sidebar:
    st.write('# Past Chats')
    if st.session_state.get('chat_id') is None:
        st.session_state.chat_id = st.selectbox(
            label='Pick a past chat',
            options=[new_chat_id] + list(past_chats.keys()),
            format_func=lambda x: past_chats.get(x, 'New Chat'),
            placeholder='_',
        )
    else:
        st.session_state.chat_id = st.selectbox(
            label='Pick a past chat',
            options=[new_chat_id, st.session_state.chat_id] + list(past_chats.keys()),
            index=1,
            format_func=lambda x: past_chats.get(x,
                                                 'New Chat' if x != st.session_state.chat_id else st.session_state.chat_title),
            placeholder='_',
        )
    st.session_state.chat_title = f'ChatSession-{st.session_state.chat_id}'

# Menambahkan CSS untuk latar belakang luar angkasa
st.markdown(
    """
    <style>
        .stApp {
            background-image: url('https://example.com/space-background.jpg');
            background-size: cover;
            background-position: center;
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Menampilkan judul utama aplikasi
st.write('# Chat with NUTRIBOT')

# Coba memuat riwayat pesan chat jika ada
try:
    st.session_state.messages = joblib.load(f'data/{st.session_state.chat_id}-st_messages')
    st.session_state.gemini_history = joblib.load(f'data/{st.session_state.chat_id}-gemini_messages')
except:
    st.session_state.messages = []
    st.session_state.gemini_history = []

# Membuat model AI generative Gemini
st.session_state.model = genai.GenerativeModel('gemini-pro')
st.session_state.chat = st.session_state.model.start_chat(history=st.session_state.gemini_history)

# Menampilkan semua pesan yang ada dalam riwayat chat
for message in st.session_state.messages:
    with st.chat_message(name=message['role'], avatar=message.get('avatar')):
        st.markdown(message['content'])

# Reaksi terhadap input pengguna
if prompt := st.chat_input('Your message here...'):
    if st.session_state.chat_id not in past_chats.keys():
        past_chats[st.session_state.chat_id] = st.session_state.chat_title
        joblib.dump(past_chats, 'data/past_chats_list')

    with st.chat_message('user'):
        st.markdown(prompt)
    st.session_state.messages.append(dict(role='user', content=prompt))

    response = st.session_state.chat.send_message(prompt, stream=True)
    with st.chat_message(name=MODEL_ROLE, avatar=AI_AVATAR_ICON):
        message_placeholder = st.empty()
        full_response = ''

        for chunk in response:
            for ch in chunk.text.split(' '):
                full_response += ch + ' '
                time.sleep(0.05)
                message_placeholder.write(full_response + '▌')
        message_placeholder.write(full_response)

    st.session_state.messages.append(dict(role=MODEL_ROLE, content=full_response, avatar=AI_AVATAR_ICON))
    st.session_state.gemini_history = st.session_state.chat.history

    joblib.dump(st.session_state.messages, f'data/{st.session_state.chat_id}-st_messages')
    joblib.dump(st.session_state.gemini_history, f'data/{st.session_state.chat_id}-gemini_messages')

import time
import os
import joblib
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

new_chat_id = f'{time.time()}'
MODEL_ROLE = 'ai'
AI_AVATAR_ICON = '🤖'

if not os.path.exists('data/'):
    os.mkdir('data/')

try:
    past_chats = joblib.load('data/past_chats_list')
except:
    past_chats = {}

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

st.write('# Chat with NUTRIBOT')

try:
    st.session_state.messages = joblib.load(f'data/{st.session_state.chat_id}-st_messages')
    st.session_state.gemini_history = joblib.load(f'data/{st.session_state.chat_id}-gemini_messages')
except:
    st.session_state.messages = []
    st.session_state.gemini_history = []

st.session_state.chat = {
    "model": "gemini-pro",
    "messages": st.session_state.gemini_history
}

for message in st.session_state.messages:
    with st.chat_message(name=message['role'], avatar=message.get('avatar')):
        st.markdown(message['content'])

if prompt := st.chat_input('Your message here...'):
    if st.session_state.chat_id not in past_chats.keys():
        past_chats[st.session_state.chat_id] = st.session_state.chat_title
        joblib.dump(past_chats, 'data/past_chats_list')

    with st.chat_message('user'):
        st.markdown(prompt)
    st.session_state.messages.append(dict(role='user', content=prompt))

    response = genai.chat(
        model=st.session_state.chat["model"],
        messages=[{"content": prompt}]
    )

    full_response = response["content"]

    with st.chat_message(name=MODEL_ROLE, avatar=AI_AVATAR_ICON):
        st.markdown(full_response)

    st.session_state.messages.append(dict(role=MODEL_ROLE, content=full_response, avatar=AI_AVATAR_ICON))
    st.session_state.gemini_history.append({"role": "user", "content": prompt})
    st.session_state.gemini_history.append({"role": MODEL_ROLE, "content": full_response})

    joblib.dump(st.session_state.messages, f'data/{st.session_state.chat_id}-st_messages')
    joblib.dump(st.session_state.gemini_history, f'data/{st.session_state.chat_id}-gemini_messages')

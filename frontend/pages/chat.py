import streamlit as st
from utils.api_client import send_chat_message, get_chat_sessions, get_chat_history

st.set_page_config(page_title="AI Assistant", layout="wide")
st.title("🤖 Manufacturing AI Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

import uuid

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Sidebar: History
st.sidebar.title("Chat History")
sessions = get_chat_sessions()

# Current session option (if not in list, e.g. new session)
options = sessions if sessions else []
if st.session_state.session_id not in options:
    options.append(st.session_state.session_id)

selected_session = st.sidebar.selectbox("Select Session", options, index=options.index(st.session_state.session_id) if st.session_state.session_id in options else 0)

if selected_session != st.session_state.session_id:
    st.session_state.session_id = selected_session
    st.session_state.messages = get_chat_history(selected_session)
    st.rerun()

st.sidebar.caption(f"Current Session: {st.session_state.session_id}")
if st.sidebar.button("New Chat"):
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.rerun()

if st.sidebar.button("Clear Chat History", type="primary"):
    from utils.api_client import delete_chat_history
    if delete_chat_history(st.session_state.session_id):
        st.session_state.messages = []
        st.success("History cleared!")
        st.rerun()
    else:
        st.error("Failed to clear history.")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask about SOPs, Diagnostics, or Maintenance..."):
    # Display user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get response
    with st.spinner("Thinking..."):
        response = send_chat_message(prompt, st.session_state.session_id)
    
    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

import streamlit as st
from agent import run_agent

# Page config
st.set_page_config(
    page_title="Summit Outfitters Support",
    page_icon="⛰️",
    layout="centered"
)

# Header
st.markdown("""
    <div style='text-align: center; padding: 1rem 0 0.5rem 0;'>
        <h1 style='font-size: 1.8rem; color: #2d5a27;'>⛰️ Summit Outfitters</h1>
        <p style='color: #666; margin-top: -0.5rem;'>Customer Support — powered by AI</p>
    </div>
    <hr style='border: none; border-top: 1px solid #ddd; margin-bottom: 1rem;'>
""", unsafe_allow_html=True)

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.conversation_history = []  # format for the API

# Starter message if chat is empty
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="⛰️"):
        st.markdown("Hi! I'm **Sierra**, your Summit Outfitters support assistant. I can help you track orders, check return eligibility, answer product questions, and more. What can I help you with today?")

# Render existing chat history
for msg in st.session_state.messages:
    avatar = "⛰️" if msg["role"] == "assistant" else "🧑"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Chat input
if user_input := st.chat_input("Ask me anything about your order or our products..."):
    # Display user message
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Add to API conversation history
    st.session_state.conversation_history.append({
        "role": "user",
        "content": user_input
    })

    # Get agent response
    with st.chat_message("assistant", avatar="⛰️"):
        with st.spinner("Sierra is looking into that..."):
            response = run_agent(st.session_state.conversation_history)
        st.markdown(response)

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.conversation_history.append({
        "role": "assistant",
        "content": response
    })

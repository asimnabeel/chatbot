import streamlit as st
from manager_agent import run

# Initialize session state for chat messages if not already present
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "ai", "content": "How can I help you?"}
    ]

# Display all chat messages from session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# Handle user input from chat input field
if user_input := st.chat_input("Enter your question..."):

    # Display user's message
    with st.chat_message("user"):
        st.markdown(user_input, unsafe_allow_html=True)
    
    # Append user's message to session state
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Show spinner while processing the query
    with st.spinner("Agent is typing...", show_time=True):
        # Process query with support agent, including chat history
        response = run(user_input)

    # Display AI's response
    with st.chat_message("ai"):
        st.markdown(response, unsafe_allow_html=True)
    
    # Append AI's response to session state
    st.session_state.messages.append({"role": "ai", "content": response})

    

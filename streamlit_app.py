import streamlit as st
import requests

# Initialize session state to store chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Sidebar for instructions or additional info
st.sidebar.title("Chat with Groq API")
st.sidebar.write("Ask any question, and I'll try to answer using the Groq API.")

# Input form for user questions
st.title("Groq API Chat App")
user_question = st.text_input("Enter your question here:")

if st.button("Submit"):
    if user_question:
        # Send the question to the Groq API
        response = requests.post(
            "https://api.groq.com/v1/ask",  # Replace with your actual Groq API endpoint
            json={"question": user_question},
            headers={"Authorization": "Bearer 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" }  # Replace with your actual API key
        )
        
        if response.status_code == 200:
            answer = response.json().get("answer", "I'm not sure, but I'll try to improve!")
            # Store the question and answer in history
            st.session_state.history.append({"question": user_question, "answer": answer})
        else:
            st.error("Failed to get a response from the Groq API. Please try again later.")

# Display chat history
if st.session_state.history:
    for chat in st.session_state.history:
        st.write("**Q:**", chat["question"])
        st.write("**A:**", chat["answer"])

# Clear chat history option
if st.button("Clear Chat History"):
    st.session_state.history.clear()
    st.write("Chat history cleared.")

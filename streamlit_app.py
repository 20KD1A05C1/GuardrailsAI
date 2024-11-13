import streamlit as st
import requests
import json

# Initialize session state for conversation history
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Set up the Streamlit interface
st.title("Chat App using Groq API")
st.write("Ask any question and get an answer!")

# Input for user's question
user_question = st.text_input("Your Question:")

# Fetch answer when the user submits a question
if st.button("Get Answer"):
    if user_question.strip():
        try:
            # Set up request payload
            payload = {
                "question": user_question,
            }
            headers = {
                "Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}",
                "Content-Type": "application/json",
            }

            # Make request to Groq API
            response = requests.post("https://api.groq.com/answer", headers=headers, json=payload)
            st.write("Response Content:", response.text)
            st.session_state.conversation.append({"question": user_question, "answer": answer})
           

            # Process response
            if response.status_code == 200:
                answer = response.json().get("answer", "No answer found.")
                # Store the question and answer in conversation history 
                st.write("Response Status Code:", response.status_code)
        
            else:
                answer = f"Error: Unable to fetch the answer. Details: {response.text}"
                st.session_state.conversation.append({"question": user_question, "answer": answer})
        except Exception as e:
            st.write(f"An error occurred: {e}")
    else:
        st.write("Please enter a question to get an answer.")

# Display the conversation history
if st.session_state.conversation:
    st.write("## Conversation History")
    for entry in st.session_state.conversation:
        st.write(f"**Question:** {entry['question']}")
        st.write(f"**Answer:** {entry['answer']}")
        st.write("---")

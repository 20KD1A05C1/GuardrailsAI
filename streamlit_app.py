import streamlit as st
import SanityClient

# Set up Sanity client
sanity = SanityClient(
    project_id="your-project-id",
    dataset="production",
    api_version="2021-03-25",
    token="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"
)

# Initialize chat history
chat_history = []

def generate_response(user_message):
    # This is a very basic example of a response generator
    # In a real application, you would integrate an AI model here
    return f"You said: '{user_message}'. I heard you!"

def save_chat_to_sanity(user_message, bot_response):
    # Save chat to Sanity
    chat_entry = {
        "_type": "chat",
        "user_message": user_message,
        "bot_response": bot_response
    }
    sanity.create(chat_entry)

st.title("Chat App")

user_input = st.text_input("Enter your message:", "")

if st.button("Send"):
    bot_response = generate_response(user_input)
    chat_history.append({"user_message": user_input, "bot_response": bot_response})
    save_chat_to_sanity(user_input, bot_response)
    st.write(f"You: {user_input}")
    st.write(f"Bot: {bot_response}")

st.subheader("Chat History")
for chat in chat_history:
    st.write(f"You: {chat['user_message']}")
    st.write(f"Bot: {chat['bot_response']}")

import streamlit as st
import groq
import requests
from urllib3.exceptions import NewConnectionError, MaxRetryError
from typing import Dict, Any

# Initialize API keys from Streamlit secrets
groq_api_key = st.secrets["groq_api_key"]
guardrails_api_key = st.secrets["guardrails_api_key"]

# Initialize Groq client
groq_client = groq.Client(api_key=groq_api_key)

# Guardrails API endpoints
GUARDRAILS_BASE_URL = "https://api.guardrailsai.com/v1"
INPUT_GUARD_URL = f"{GUARDRAILS_BASE_URL}/guard/input"
OUTPUT_GUARD_URL = f"{GUARDRAILS_BASE_URL}/guard/output"

# Guardrails headers
guardrails_headers = {
    "Authorization": f"Bearer {guardrails_api_key}",
    "Content-Type": "application/json"
}

def handle_guard_error(guard_result):
    """
    Handle errors that occur during input or output guard checks
    """
    if not guard_result:
        return "There was an error checking the message. Please try again later."
    
    if not guard_result.get("passed"):
        violations = guard_result.get("violations", [])
        return f"Content blocked due to: {', '.join(violations)}"
    
    return None

def apply_input_guard(user_input: str) -> Dict[str, Any]:
    """
    Apply input guard using Guardrails API to validate and sanitize user input
    """
    try:
        payload = {
            "input": user_input,
            "guards": [
                "no_harassment",
                "no_hate_speech",
                "no_profanity",
                "no_sexual_content",
                "no_violence"
            ]
        }
        
        response = requests.post(
            INPUT_GUARD_URL,
            headers=guardrails_headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, NewConnectionError, MaxRetryError) as e:
        st.error(f"Input guard error: {str(e)}")
        return None

def apply_output_guard(ai_response: str) -> Dict[str, Any]:
    """
    Apply output guard using Guardrails API to validate and sanitize AI response
    """
    try:
        payload = {
            "output": ai_response,
            "guards": [
                "no_harassment",
                "no_hate_speech",
                "no_profanity",
                "no_sexual_content",
                "no_violence",
                "factual_accuracy",
                "response_relevance"
            ]
        }
        
        response = requests.post(
            OUTPUT_GUARD_URL,
            headers=guardrails_headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, NewConnectionError, MaxRetryError) as e:
        st.error(f"Output guard error: {str(e)}")
        return None

def get_ai_response(prompt: str) -> str:
    """
    Get response from Groq API
    """
    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful, respectful, and honest assistant. Always provide accurate and relevant information, and acknowledge when you're not sure about something."},
                {"role": "user", "content": prompt}
            ],
            model="mixtral-8x7b-32768",
            max_tokens=800,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Groq API error: {str(e)}")
        return None

def process_message(user_input: str) -> str:
    """
    Process user message through input guard, AI, and output guard
    """
    # Apply input guard
    input_guard_result = apply_input_guard(user_input)
    input_guard_error = handle_guard_error(input_guard_result)
    if input_guard_error:
        return input_guard_error
    
    # Get AI response
    ai_response = get_ai_response(user_input)
    if not ai_response:
        return "I apologize, but I couldn't generate a response at this time. Please try again."
    
    # Apply output guard
    output_guard_result = apply_output_guard(ai_response)
    output_guard_error = handle_guard_error(output_guard_result)
    if output_guard_error:
        return output_guard_error
    
    return ai_response

def initialize_session_state():
    """
    Initialize session state variables
    """
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation_started" not in st.session_state:
        st.session_state.conversation_started = False

def display_chat_interface():
    """
    Display and handle the chat interface
    """
    st.title("AI Chat Assistant")
    st.caption("Ask me anything! Your messages are protected by input and output guards.")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Get user input
    if prompt := st.chat_input("Type your message here..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = process_message(prompt)
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

def main():
    # Set page config
    st.set_page_config(
        page_title="AI Chat Assistant",
        page_icon="💭",
        layout="centered"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Display chat interface
    display_chat_interface()
    
    # Add a footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>This chat is protected by input and output guards for safety and quality.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()

import time
import requests
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

st.set_page_config(page_title="Streaming bot", page_icon="🤖")
st.title("Streaming bot")


def send_chat_completion(query: str) -> dict:
    url = "http://localhost:8000/v1/chat/completions"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "string",
        "messages": [
            {
                "role": "client",
                "content": query  # **여기에 입력받은 값이 들어갑니다**
            }
        ],
        "temperature": 0
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.status_code, "message": response.text}


def get_response(user_query, chat_history):
    stream = send_chat_completion(user_query)
    content = stream["choices"][0]["message"]["content"]
    for word in content.split(" "):
        yield word + " "
        time.sleep(0.02)

    # session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [AIMessage(content="안녕 나는 Chatbot이야 무엇을 도와줄까?")]

# conversation
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)

# user input
user_query = st.chat_input("Type your message here...")
if user_query is not None and user_query != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    with st.chat_message("Human"):
        st.markdown(user_query)
    with st.chat_message("AI"):
        response = st.write_stream(get_response(user_query, st.session_state.chat_history))
    st.session_state.chat_history.append(AIMessage(content=response))
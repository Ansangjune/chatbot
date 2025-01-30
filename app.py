import os
from dotenv import load_dotenv
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from pinecone import Pinecone
from langchain import vectorstores
from langchain.embeddings.openai import OpenAIEmbeddings

load_dotenv()

embed_model = OpenAIEmbeddings(model="text-embedding-ada-002")
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("the-democraticparty")
vectorstore = vectorstores.Pinecone(index, embed_model.embed_query, "text")
chat = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model='gpt-3.5-turbo', streaming=True)

st.set_page_config(page_title="Streaming bot", page_icon="🤖")
st.title("Streaming bot")

def augment_prompt(query: str):
    results = vectorstore.similarity_search(query, k=3)
    source_knowledge = "\n".join([x.page_content for x in results])
    augmented_prompt = f"""Using the contexts below, answer the query in korean.
    Contexts:
    {source_knowledge}
    Query: {query}"""
    return augmented_prompt

def get_response(user_query, chat_history):
    prompt = HumanMessage(content=augment_prompt(user_query))
    ai_history = chat_history[:-1] + [prompt]
    stream = chat.invoke(ai_history)
    for chunk in stream:
        if chunk[0] == "content":
            yield chunk[1]

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
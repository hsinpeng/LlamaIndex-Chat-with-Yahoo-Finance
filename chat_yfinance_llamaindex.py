import streamlit as st
import pandas as pd
import os

from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from llama_index.core.agent import ReActAgent
from llama_index.tools.yahoo_finance import YahooFinanceToolSpec


st.set_page_config(page_title="LlamaIndex: Chat with Yahoo Finance", page_icon="🦜")
st.title(":bar_chart: LlamaIndex: Chat with Yahoo Finance")


openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
if "messages" not in st.session_state or st.sidebar.button("Clear conversation history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# Sidebar for Question Examples
with st.sidebar:
    st.sidebar.markdown("### You may like to talk about:")
    questions_list = [
        "What is the current price of Google?", 
        "The summary of the latest recommendations of CocaCola.",
        "What is the quarterly cash flow for Nvidia?", 
        "Give me information about Amazon.", 
        "What are the recent analyst recommendations for Tesla?",
        "How many shares did Apple have outstanding between January 1, 2023, and December 31, 2023?", 
        "Give me dividends and splits for Microsoft for 2022.",
        "Can you provide the quarterly balance sheet for Google?", 
        "What are the latest news report about Tesla?",
        "What are the sustainability scores of CocaCola?",
    ]
    # Display Question Examples in the Sidebar
    for question in questions_list:
        st.markdown(f"- {question}")


for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="What finance topic you like to talk about?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    # settings of the openai model
    if ("model_init" not in st.session_state) or (st.session_state["model_init"] is False):
        llm = OpenAI(model="gpt-4-turbo", api_key=openai_api_key, temperature=0)
        Settings.llm = llm
        st.session_state["model_init"] = True
    
    # build an agent
    if "chat_engine" not in st.session_state:
        finance_tools = YahooFinanceToolSpec().to_tool_list()
        st.session_state["chat_engine"] = ReActAgent.from_tools(finance_tools, verbose=True)

    yfinance_agent = st.session_state["chat_engine"]

    with st.chat_message("assistant"):
        response = yfinance_agent.stream_chat(prompt)
        response_str = ""
        response_container = st.empty()
        for token in response.response_gen:
            response_str += token
            response_container.write(response_str)
        # st.write(response.response)
        st.session_state.messages.append({"role": "assistant", "content": response.response})
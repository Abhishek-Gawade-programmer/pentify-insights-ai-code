import nest_asyncio
import streamlit as st
from agents import get_sql_agent
from agno.agent import Agent
from agno.utils.log import logger
from utils import (
    CUSTOM_CSS,
    about_widget,
    add_message,
    display_tool_calls,
    rename_session_widget,
    session_selector_widget,
    sidebar_widget,
)


nest_asyncio.apply()

# Page configuration
st.set_page_config(
    page_title="Collaborate Global Insights",
    page_icon=":briefcase:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load custom CSS with dark mode support
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def main() -> None:
    ####################################################################
    # App header
    ####################################################################
    st.markdown(
        "<h1 class='main-title'>Collaborate Global Insights</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='subtitle'>Your intelligent business data analyst </p>",
        unsafe_allow_html=True,
    )

    ####################################################################
    # Initialize Agent
    ####################################################################
    sql_agent: Agent
    if "sql_agent" not in st.session_state or st.session_state["sql_agent"] is None:
        logger.info("---*--- Creating new SQL agent ---*---")
        sql_agent = get_sql_agent()
        st.session_state["sql_agent"] = sql_agent
    else:
        sql_agent = st.session_state["sql_agent"]

    ####################################################################
    # Load Agent Session from the database
    ####################################################################
    try:
        st.session_state["sql_agent_session_id"] = sql_agent.load_session()
    except Exception as e:
        st.warning("Could not create Agent session, is the database running?")
        raise e

    ####################################################################
    # Load runs from memory
    ####################################################################
    agent_runs = sql_agent.memory.runs
    if len(agent_runs) > 0:
        logger.debug("Loading run history")
        st.session_state["messages"] = []
        for _run in agent_runs:
            if _run.message is not None:
                add_message(_run.message.role, _run.message.content)
            if _run.response is not None:
                add_message("assistant", _run.response.content, _run.response.tools)
    else:
        logger.debug("No run history found")
        st.session_state["messages"] = []

    ####################################################################
    # Sidebar
    ####################################################################
    sidebar_widget()

    ####################################################################
    # Get user input
    ####################################################################
    if prompt := st.chat_input("👋 Ask me about Collaborate Global's database!"):
        add_message("user", prompt)

    ####################################################################
    # Display chat history
    ####################################################################
    for message in st.session_state["messages"]:
        if message["role"] in ["user", "assistant"]:
            _content = message["content"]
            if _content is not None:
                with st.chat_message(message["role"]):
                    # Display tool calls if they exist in the message
                    if "tool_calls" in message and message["tool_calls"]:
                        display_tool_calls(st.empty(), message["tool_calls"])
                    st.markdown(_content)

    ####################################################################
    # Generate response for user message
    ####################################################################
    last_message = (
        st.session_state["messages"][-1] if st.session_state["messages"] else None
    )
    if last_message and last_message.get("role") == "user":
        question = last_message["content"]
        with st.chat_message("assistant"):
            # Create container for tool calls
            tool_calls_container = st.empty()
            resp_container = st.empty()
            with st.spinner("🤔 Thinking..."):
                response = ""
                try:
                    # Run the agent and stream the response
                    run_response = sql_agent.run(question, stream=True)
                    for _resp_chunk in run_response:
                        # Display tool calls if available
                        if _resp_chunk.tools and len(_resp_chunk.tools) > 0:
                            display_tool_calls(tool_calls_container, _resp_chunk.tools)

                        # Display response
                        if _resp_chunk.content is not None:
                            response += _resp_chunk.content
                            resp_container.markdown(response)

                    add_message("assistant", response, sql_agent.run_response.tools)
                except Exception as e:
                    error_message = f"Sorry, I encountered an error: {str(e)}"
                    add_message("assistant", error_message)
                    st.error(error_message)

    ####################################################################
    # Session selector
    ####################################################################
    session_selector_widget(sql_agent)
    rename_session_widget(sql_agent)

    ####################################################################
    # About section
    ####################################################################
    about_widget()


if __name__ == "__main__":
    main()

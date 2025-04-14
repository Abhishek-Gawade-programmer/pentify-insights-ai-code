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
import uuid
import asyncio


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
    # Model selector
    ####################################################################
    model_options = {
        "gpt-4o": "openai:gpt-4o",
        "gemini-2.0-flash-exp": "google:gemini-2.0-flash-exp",
        "claude-3-5-sonnet": "anthropic:claude-3-5-sonnet-20241022",
    }
    selected_model = st.sidebar.selectbox(
        "Select a model",
        options=list(model_options.keys()),
        index=0,
        key="model_selector",
    )
    model_id = model_options[selected_model]

    ####################################################################
    # Initialize Agent
    ####################################################################
    user_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    if (
        "sql_agent" not in st.session_state
        or st.session_state["sql_agent"] is None
        or st.session_state.get("current_model") != model_id
    ):
        logger.info("---*--- Creating new SQL agent ---*---")
        st.session_state["sql_agent"] = True
        st.session_state["current_model"] = model_id
        st.session_state["user_id"] = user_id
        st.session_state["session_id"] = session_id
    else:
        user_id = st.session_state["user_id"]
        session_id = st.session_state["session_id"]

    ####################################################################
    # Load Agent Session from the database
    ####################################################################
    try:
        st.session_state["sql_agent_session_id"] = session_id
    except Exception:
        st.warning("Could not create Agent session, is the database running?")
        return

    ####################################################################
    # Load runs from memory
    ####################################################################
    try:
        # Get a temporary agent to access the memory
        temp_agent = asyncio.run(
            get_sql_agent(
                user_id=user_id,
                session_id=session_id,
                model_id=model_id,
            )
        )
        agent_runs = temp_agent.memory.runs if hasattr(temp_agent, "memory") else []

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
    except Exception as e:
        logger.error(f"Error loading run history: {str(e)}")
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
                    # Run the agent and get the response using the new method
                    AGENT_RESPONSE = asyncio.run(
                        get_sql_agent(
                            user_id=user_id,
                            session_id=session_id,
                            model_id=model_id,
                            message=question,
                        )
                    )

                    # Display response
                    response = AGENT_RESPONSE
                    resp_container.markdown(response)

                    add_message("assistant", response)
                except Exception as e:
                    error_message = f"Sorry, I encountered an error: {str(e)}"
                    add_message("assistant", error_message)
                    st.error(error_message)

    ####################################################################
    # Session selector
    ####################################################################
    # Get a temporary agent for session operations
    try:
        temp_agent = asyncio.run(
            get_sql_agent(
                user_id=user_id,
                session_id=session_id,
                model_id=model_id,
            )
        )
        session_selector_widget(temp_agent, model_id)
        rename_session_widget(temp_agent)
    except Exception as e:
        st.error(f"Error loading session operations: {str(e)}")

    ####################################################################
    # About section
    ####################################################################
    about_widget()


if __name__ == "__main__":
    main()

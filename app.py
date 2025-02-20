import os
import sys
import streamlit as st
from swarm import Swarm, Agent
import uuid
from mem0 import Memory

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents import manager

config = {
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "chatbot_memory",
            "path": "./chroma_db",
        },
    },
    "version": "v1.1"
}

# Initialize Swarm client
client = Swarm()
memory = Memory.from_config(config)

# Initialize session state for chat history and thread ID
if "messages" not in st.session_state:
    st.session_state.messages = []

# Generate a new thread ID for each run
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())  # Generate a unique thread ID

def main():
    # Set page configuration
    st.set_page_config(
        page_title="FootGen AI",
        page_icon="🤖",
        layout="wide"
    )
    
    # Header
    st.title("FootGen AI")
    st.markdown(f"**Thread ID:** {st.session_state.thread_id}")  # Display the thread ID
    st.markdown("---")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if user_input := st.chat_input("Type your message here..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})
        # Fetch related memories
        memories = memory.search(
            user_input, 
            user_id=st.session_state.thread_id
        )

        if memories['results']!= []:
            previous_memories = [m['memory'] for m in memories['results']]
            if previous_memories:
                user_input = f"User input: {user_input}\nPrevious memories: {previous_memories}"
        # Format input for Swarm
        inputs = [{"role": "user", "content": user_input}]

        # Add user message to memory
        memory.add(
            user_input, 
            user_id=st.session_state.thread_id, 
            metadata={"category": "user"}
        )
        # Get response from Swarm
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = client.run(agent=manager, messages=inputs)
                if isinstance(response, Agent):
                    selected_agent = response
                    result = selected_agent.functions
                    st.markdown(f"{result}")
                    # Add response to history
                    memory.add(
                        str(result), 
                        user_id=st.session_state.thread_id, 
                        metadata={"category": "assistant"}
                    )
                    st.session_state.messages.append({"role": "assistant", "content": str(result)})
                else:
                    response_content = response.messages[-1]['content']
                    st.markdown(response_content)
                    # Add response to history
                    memory.add(
                        response_content, 
                        user_id=st.session_state.thread_id, 
                        metadata={"category": "assistant"}
                    )
                    st.session_state.messages.append({"role": "assistant", "content": response_content})

if __name__ == "__main__":
    main()


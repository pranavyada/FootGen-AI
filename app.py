import os
import sys
import streamlit as st
from swarm import Swarm, Agent
import uuid
from mem0 import Memory
import json
from datetime import datetime

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

# Add this near the top of the file, after imports
if not os.path.exists("conversations"):
    os.makedirs("conversations")

# Add these functions at the top level, after the imports
def save_conversation(messages, thread_id):
    """Save conversation history to a JSON file"""
    
    filename = f"conversations/{thread_id}.json"
    with open(filename, "w") as f:
        json.dump({
            "thread_id": thread_id,
            "timestamp": datetime.now().isoformat(),
            "messages": messages
        }, f)

def load_conversation(thread_id):
    """Load conversation history from a JSON file"""
    filename = f"conversations/{thread_id}.json"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            data = json.load(f)
            return data["messages"]
    return []

def format_timestamp(timestamp_str):
    """Format ISO timestamp to a more readable format"""
    dt = datetime.fromisoformat(timestamp_str)
    return dt.strftime("%Y-%m-%d %H:%M")

def load_conversation_preview(thread_id):
    """Load conversation preview from a JSON file"""
    filename = f"conversations/{thread_id}.json"
    if os.path.exists(filename):
        with open(filename, "r") as f:
            data = json.load(f)
            # Get the first message content (truncated) and timestamp
            first_message = data["messages"][0]["content"] if data["messages"] else "Empty conversation"
            preview = first_message[:50] + "..." if len(first_message) > 50 else first_message
            return {
                "preview": preview
            }
    return None

# Modify the session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
    # Try to load existing conversation for new thread
    st.session_state.messages = load_conversation(st.session_state.thread_id)

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

    # Replace the dropdown with a list of conversations
    st.sidebar.title("Past Conversations")
    
    # Add New Chat button at the top of sidebar
    if st.sidebar.button("New Chat", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    st.sidebar.markdown("---")

    # Show saved conversations as a list
    conversation_files = [f.replace(".json", "") for f in os.listdir("conversations") if f.endswith(".json")]
    
    for thread_id in sorted(conversation_files, reverse=True):
        preview = load_conversation_preview(thread_id)
        if preview:
            with st.sidebar.container():
                col1, col2 = st.sidebar.columns([7, 3])
                with col1:
                    if st.button(
                        f"📝 {preview['preview']}\n\n",
                        key=thread_id,
                        use_container_width=True
                    ):
                        st.session_state.thread_id = thread_id
                        st.session_state.messages = load_conversation(thread_id)
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"delete_{thread_id}", help="Delete conversation"):
                        os.remove(f"conversations/{thread_id}.json")
                        if thread_id == st.session_state.thread_id:
                            st.session_state.thread_id = str(uuid.uuid4())
                            st.session_state.messages = []
                        st.rerun()
                st.sidebar.markdown("---")

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
                    # Save conversation after adding the message
                    save_conversation(st.session_state.messages, st.session_state.thread_id)
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
                    # Save conversation after adding the message
                    save_conversation(st.session_state.messages, st.session_state.thread_id)

if __name__ == "__main__":
    main()


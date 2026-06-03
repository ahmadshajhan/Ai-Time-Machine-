import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# ==========================================
# 1. INITIALIZATION & CONFIGURATION
# ==========================================
load_dotenv()

# We set layout to "centered" for that clean, focused Claude look
st.set_page_config(
    page_title="AI Time Machine",
    page_icon="💬",
    layout="centered",
    initial_sidebar_state="collapsed" 
)

# ==========================================
# 2. CLAUDE DARK THEME CSS
# ==========================================
def inject_claude_css():
    st.markdown("""
    <style>
        /* Base Theme - Claude Dark Mode */
        .stApp {
            background-color: #212121 !important;
            color: #ececec !important;
            font-family: 'Söhne', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        /* Center the chat and add spacing */
        .block-container {
            padding-top: 3rem !important;
            max-width: 800px !important;
        }
        
        /* Hide Streamlit Header & Footer & Sidebar */
        [data-testid="stHeader"] { display: none !important; }
        footer { visibility: hidden !important; }
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        
        /* Chat Message Styling */
        [data-testid="stChatMessage"] {
            background-color: transparent !important;
            border: none !important;
            padding: 1rem 0 !important;
        }
        
        /* Avatars */
        [data-testid="chatAvatarIcon-user"] {
            background-color: #4a4a4a !important;
            color: white !important;
        }
        [data-testid="chatAvatarIcon-assistant"] {
            background-color: #d97757 !important; /* Claude's signature accent color */
            color: white !important;
        }

        /* Chat Input Box */
        [data-testid="stChatInput"] {
            background-color: #2f2f2f !important;
            border: 1px solid #424242 !important;
            border-radius: 12px !important;
            padding-bottom: 5px !important;
        }
        
        [data-testid="stChatInput"] textarea {
            color: #ececec !important;
        }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. MAIN APP LOGIC
# ==========================================
def main():
    inject_claude_css()
    
    # Minimalist Title
    st.markdown("<h2 style='text-align: center; color: #ececec; margin-bottom: 2rem; font-weight: 500;'>AI Time Machine</h2>", unsafe_allow_html=True)

    # API Key Verification
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        st.error("server crash")
        st.stop()

    # Initialize LLM
    try:
        llm = ChatGroq(
            api_key=api_key,
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=1024
        )
    except Exception as e:
        st.error(f"Failed to initialize Groq client: {e}")
        st.stop()

    # Initialize Session State
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
        # Hidden System Prompt
        st.session_state.system_prompt = SystemMessage(
            content="You are a highly intelligent, concise, and helpful AI assistant."
        )
        
        # First greeting
        st.session_state.messages.append(AIMessage(content="Hello. How can I help you today?"))

    # Render Chat History
    for msg in st.session_state.messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.markdown(msg.content)

    # Handle User Input
    if user_input := st.chat_input("Message AI..."):
        
        # 1. Append and show user message
        st.session_state.messages.append(HumanMessage(content=user_input))
        with st.chat_message("user"):
            st.markdown(user_input)

        # 2. Build conversation context
        conversation = [st.session_state.system_prompt] + st.session_state.messages

        # 3. Fetch and show AI response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                response = llm.invoke(conversation)
                message_placeholder.markdown(response.content)
                st.session_state.messages.append(AIMessage(content=response.content))
            except Exception as e:
                message_placeholder.error(f"API Error: {e}")

if __name__ == "__main__":
    main()
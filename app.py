import streamlit as st
from dotenv import load_dotenv

# Import your existing backend functions
from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarizer import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

# Load environment variables (API keys)
load_dotenv()

# --- Page Configuration ---
st.set_page_config(page_title="AI Video Assistant", page_icon="🤖", layout="wide")

# --- Session State Management ---
# We use session state so the pipeline doesn't re-run every time you type in the chat
if "processed_data" not in st.session_state:
    st.session_state.processed_data = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Sidebar for Inputs ---
with st.sidebar:
    st.header("⚙️ Configuration")
    source = st.text_input("YouTube URL or Local File:", placeholder="https://youtu.be/...")
    language = st.selectbox("Language:", ["english", "hinglish"])
    
    process_btn = st.button("🚀 Analyze Video", use_container_width=True)

# --- Main App Area ---
st.title("🤖 AI Video & Meeting Assistant")

# 1. Processing Logic
if process_btn:
    if not source:
        st.sidebar.error("Please enter a URL or file path.")
    else:
        # Use st.status to show step-by-step progress similar to your CLI prints
        with st.status("Pipeline Running...", expanded=True) as status:
            st.write("📥 Downloading and chunking audio...")
            chunks = process_input(source)
            
            st.write("🎙️ Transcribing audio (this may take a bit)...")
            transcript = transcribe_all(chunks, language)
            
            st.write("🧠 Generating summary and insights...")
            title = generate_title(transcript)
            summary = summarize(transcript)
            action_items = extract_action_items(transcript)
            key_decisions = extract_key_decisions(transcript)
            open_questions = extract_questions(transcript)
            
            st.write("📚 Building RAG database for chat...")
            rag_chain = build_rag_chain(transcript)
            
            status.update(label="✅ Analysis Complete!", state="complete", expanded=False)

        # Save all results to session state
        st.session_state.processed_data = {
            "title": title,
            "transcript": transcript,
            "summary": summary,
            "action_items": action_items,
            "key_decisions": key_decisions,
            "open_questions": open_questions,
            "rag_chain": rag_chain
        }
        # Reset chat history for the new video
        st.session_state.chat_history = []

# 2. Display Results (Only if data exists in session state)
if st.session_state.processed_data:
    data = st.session_state.processed_data
    
    st.header(f"📌 {data['title']}")
    
    # Create tabs for clean organization
    tab_dash, tab_chat, tab_transcript = st.tabs([
        "📊 Dashboard", 
        "💬 Chat with Video", 
        "📝 Raw Transcript"
    ])
    
    # --- Tab 1: Dashboard Insights ---
    with tab_dash:
        st.subheader("📋 Summary")
        st.write(data["summary"])
        
        st.divider()
        
        # Use columns for side-by-side layout
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("✅ Action Items")
            st.info(data["action_items"])
            
        with col2:
            st.subheader("🔑 Key Decisions")
            st.success(data["key_decisions"])
            
        st.subheader("❓ Open Questions")
        st.warning(data["open_questions"])
        
    # --- Tab 2: Interactive RAG Chat ---
    with tab_chat:
        st.subheader("💬 Ask questions about the video")
        
        # Display existing chat history
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        # Chat input at the bottom
        if user_q := st.chat_input("E.g., What were the main technical challenges discussed?"):
            # 1. Append and show user message
            st.session_state.chat_history.append({"role": "user", "content": user_q})
            with st.chat_message("user"):
                st.write(user_q)
                
            # 2. Generate and show AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer = ask_question(data["rag_chain"], user_q)
                    st.write(answer)
            # 3. Append AI response to history
            st.session_state.chat_history.append({"role": "assistant", "content": answer})

    # --- Tab 3: Raw Text ---
    with tab_transcript:
        st.text_area("Full Transcript", data["transcript"], height=400)
        
else:
    # Shown when the app first loads
    st.info("👈 Enter a video URL in the sidebar and click 'Analyze Video' to get started.")
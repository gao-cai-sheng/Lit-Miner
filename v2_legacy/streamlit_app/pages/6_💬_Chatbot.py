"""
💬 Chatbot - Periodontal Disease Expert
RAG-based Q&A system with source citations
"""

import streamlit as st
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.chatbot import RAGEngine, ConversationManager, AnswerGenerator

st.set_page_config(
    page_title="Chatbot - Lit-Miner",
    page_icon="💬",
    layout="wide"
)

# Initialize components
@st.cache_resource
def init_chatbot():
    """Initialize chatbot components (cached)"""
    try:
        rag_engine = RAGEngine()
        answer_gen = AnswerGenerator()
        return rag_engine, answer_gen, None
    except Exception as e:
        return None, None, str(e)

rag_engine, answer_gen, error = init_chatbot()

# Initialize conversation manager in session state
if 'conv_manager' not in st.session_state:
    st.session_state.conv_manager = ConversationManager()
    st.session_state.conv_manager.create_session()

conv_manager = st.session_state.conv_manager

# Sidebar
with st.sidebar:
    st.header("⚙️ Chatbot Settings")
    
    if error:
        st.error(f"❌ 初始化失败: {error}")
        st.info("💡 请先运行知识库构建")
    elif rag_engine:
        stats = rag_engine.get_collection_stats()
        st.success(f"✅ 知识库已加载")
        st.metric("文献片段数", stats['total_chunks'])
        
        if stats['sample_documents']:
            with st.expander("📚 示例文献"):
                for doc in stats['sample_documents']:
                    st.caption(f"• {doc['title'][:40]}... ({doc['year']})")
    
    st.divider()
    
    # Session management
    st.subheader("💬 对话管理")
    
    if st.button("🔄 新建对话", use_container_width=True):
        conv_manager.save_session()  # Save current
        conv_manager.create_session()  # Create new
        st.rerun()
    
    # Show current session info
    summary = conv_manager.get_session_summary()
    if summary:
        st.caption(f"当前对话: {summary}")
    
    # List previous sessions
    sessions = conv_manager.list_sessions()
    if len(sessions) > 1:  # More than current session
        st.divider()
        st.caption("📜 历史对话")
        for session in sessions[:5]:  # Show last 5
            if st.button(
                f"{session['session_id']} ({session['message_count']} 条)",
                key=f"session_{session['session_id']}",
                use_container_width=True
            ):
                conv_manager.save_session()
                conv_manager.load_session(session['session_id'])
                st.rerun()

# Main area
st.title("💬 Periodontal Disease Expert")
st.markdown("基于核心文献的牙周病学专业问答系统")

if error:
    st.error(f"系统未就绪: {error}")
    st.info("""
    请先构建知识库：
    ```python
    from core.chatbot import KnowledgeBuilder
    builder = KnowledgeBuilder()
    builder.build_from_directory("data/pdfs/chatbot_knowledge")
    ```
    """)
    st.stop()

# Display conversation history
st.divider()
history = conv_manager.get_history(last_n=20)

if not history:
    st.info("👋 您好！我是牙周病学专家助手。请输入您的问题。")
else:
    # Display messages
    for msg in history:
        with st.chat_message(msg['role']):
            st.markdown(msg['content'])
            
            # Show sources if available
            if msg['role'] == 'assistant' and 'sources' in msg:
                with st.expander("📚 引用来源"):
                    for src in msg['sources']:
                        st.caption(
                            f"[{src['index']}] {src['title']} - "
                            f"{src['authors']} ({src['year']})"
                        )

# Chat input
user_input = st.chat_input("请输入您的问题...")

if user_input:
    # Add user message to history
    conv_manager.add_message("user", user_input)
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("🤔 思考中..."):
            # Retrieve relevant docs
            retrieved = rag_engine.retrieve(
                user_input,
                conversation_history=conv_manager.get_history(last_n=5)
            )
            
            if not retrieved:
                response = "抱歉，我在知识库中没有找到相关信息。请尝试换一个问题。"
                sources = []
            else:
                # Generate answer
                result = answer_gen.generate(
                    question=user_input,
                    retrieved_docs=retrieved,
                    conversation_history=conv_manager.get_history(last_n=5)
                )
                
                response = result['answer']
                sources = result['sources']
            
            # Display response
            st.markdown(response)
            
            # Display sources
            if sources:
                with st.expander("📚 引用来源"):
                    for src in sources:
                        st.caption(
                            f"[{src['index']}] {src['title']} - "
                            f"{src['authors']} ({src['year']})"
                        )
            
            # Add to conversation history
            conv_manager.add_message("assistant", response, sources=sources)
            
            # Auto-save session
            conv_manager.save_session()

# Footer
st.divider()
st.caption("💬 Chatbot | Lit-Miner | Powered by RAG + DeepSeek")

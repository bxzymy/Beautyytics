import streamlit as st





TEXT_CONTENT = {
    "zh": {
        "analysis_page_title": "妆策灵析",
        "back_to_home": "← 返回主页",
        "view_history": "查看历史对话",
        "clear_history": "清除对话历史",
        "history_title": "历史对话记录",
        "no_history": "暂无历史对话",
    },
    "en": {
        "analysis_page_title": "Beautyytics",
        "back_to_home": "← Back to Home",
        "view_history": "View History",
        "clear_history": "Clear History",
        "history_title": "Conversation History",
        "no_history": "No history yet",
    }
}



def show_history_panel():
    texts = TEXT_CONTENT[st.session_state.lang]

    with st.sidebar.expander(f"📜 {texts['history_title']}", expanded=st.session_state.show_history):
        if not st.session_state.ui_messages:
            st.info(texts["no_history"])
        else:
            # 只显示用户问题和AI的简要回答
            for i, msg in enumerate(st.session_state.ui_messages):
                if msg["role"] == "user":
                    query = msg.get("content", "")
                    # 找到对应的AI回复
                    ai_response = ""
                    if i + 1 < len(st.session_state.ui_messages) and st.session_state.ui_messages[i + 1][
                        "role"] == "assistant":
                        ai_msg = st.session_state.ui_messages[i + 1]
                        if "data_analysis_text" in ai_msg:
                            ai_response = ai_msg["data_analysis_text"]
                        elif "content" in ai_msg:
                            ai_response = ai_msg["content"]

                    # 显示历史条目
                    st.markdown(
                        f"""
                        <div class="history-item" onclick="streamlitScriptRunner.setComponentValue({i});">
                            <div class="history-query">👤 {query[:50]}{'...' if len(query) > 50 else ''}</div>
                            <div class="history-response">🤖 {ai_response[:70]}{'...' if len(ai_response) > 70 else ''}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


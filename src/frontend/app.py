import streamlit as st
import asyncio
import sys
import os
from typing import List, Dict
import time

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

try:
    from src.DeepResearch.deep_research import DeepResearch
except ImportError as e:
    st.error(f"无法导入DeepResearch模块: {e}")
    st.error("请确保项目路径配置正确，并且所有依赖都已安装。")
    
    with st.expander("🔧 故障排除指南"):
        st.markdown("""
        **可能的解决方案:**
        
        1. **检查项目结构**: 确保在正确的项目根目录运行
        2. **安装依赖**: 运行 `pip install -r requirements.txt`
        3. **配置文件**: 确保 `src/DeepResearch/config/config.yaml` 存在且配置正确
        4. **API密钥**: 检查配置文件中的API密钥是否正确设置
        
        **配置文件示例:**
        ```yaml
        agents:
          critic_agent:
            model: "deepseek-chat"
          research_agent:
            model: "deepseek-chat"
            max_steps: 3
        
        models:
          - models: ["deepseek-chat"]
            model_platform: "deepseek"
            platform_api_key: "your-api-key-here"
            temperature: 0.7
        ```
        """)
    st.stop()

# 页面配置
st.set_page_config(
    page_title="DeepResearch AI 研究助手",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        background-color: #f8f9fa;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    
    .assistant-message {
        background-color: #f1f8e9;
        border-left-color: #4caf50;
    }
    
    .stTextInput > div > div > input {
        border-radius: 20px;
    }
    
    .research-step {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #fafafa;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """初始化会话状态"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "research_history" not in st.session_state:
        st.session_state.research_history = []
    if "is_researching" not in st.session_state:
        st.session_state.is_researching = False

def display_message(message: Dict[str, str], is_user: bool = False):
    """显示消息"""
    css_class = "user-message" if is_user else "assistant-message"
    icon = "🧑‍💼" if is_user else "🤖"
    
    with st.container():
        st.markdown(f"""
        <div class="chat-message {css_class}">
            <strong>{icon} {"您" if is_user else "DeepResearch AI"}:</strong><br>
            {message}
        </div>
        """, unsafe_allow_html=True)

def run_research_sync(query: str, max_steps: int, progress_container):
    """同步运行研究任务"""
    try:
        deep_research = DeepResearch(max_steps=max_steps)
        
        full_response = ""
        
        # 创建异步函数来处理流式输出
        async def async_research():
            nonlocal full_response
            async for response_chunk in deep_research.execute(
                query=query, 
                history=st.session_state.research_history
            ):
                full_response += response_chunk
                # 实时更新显示内容
                progress_container.markdown(full_response)
        
        # 运行异步研究
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(async_research())
        finally:
            loop.close()
        
        return full_response
        
    except Exception as e:
        st.error(f"研究过程中出现错误: {str(e)}")
        return None

def main():
    """主函数"""
    initialize_session_state()
    
    # 页面标题
    st.markdown("""
    <div class="main-header">
        <h1>🔍 DeepResearch AI 研究助手</h1>
        <p>基于多智能体协作的深度研究工具</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 侧边栏配置
    with st.sidebar:
        st.header("⚙️ 研究配置")
        
        max_steps = st.slider(
            "最大研究步骤",
            min_value=1,
            max_value=20,
            value=10,
            help="设置研究的最大迭代步骤数"
        )
        
        st.markdown("---")
        
        # 清除历史按钮
        if st.button("🗑️ 清除对话历史", type="secondary"):
            st.session_state.messages = []
            st.session_state.research_history = []
            st.rerun()
        
        st.markdown("---")
        
        # 使用说明
        with st.expander("📖 使用说明"):
            st.markdown("""
            **DeepResearch AI** 是一个基于多智能体协作的深度研究工具：
            
            1. **研究智能体**: 负责信息收集和初步分析
            2. **批判智能体**: 进行批判性思考和深度分析
            3. **协作机制**: 两个智能体交替工作，逐步深化研究
            
            **使用方法**:
            - 在下方输入框中输入您的研究问题
            - 点击发送或按Enter键开始研究
            - 系统将自动进行多轮深度分析
            - 支持实时查看研究进展
            """)
    
    # 主要内容区域
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 显示历史对话
        if st.session_state.messages:
            st.subheader("💬 对话历史")
            for message in st.session_state.messages:
                if message["role"] == "user":
                    display_message(message["content"], is_user=True)
                else:
                    st.markdown(message["content"])
        
        # 输入区域
        st.markdown("---")
        
        # 创建输入表单
        with st.form(key="research_form", clear_on_submit=True):
            user_input = st.text_area(
                "请输入您的研究问题:",
                placeholder="例如: 中国新能源行业在未来五年的发展趋势",
                height=100,
                disabled=st.session_state.is_researching
            )
            
            col_submit, col_status = st.columns([1, 3])
            
            with col_submit:
                submit_button = st.form_submit_button(
                    "🚀 开始研究",
                    disabled=st.session_state.is_researching,
                    type="primary"
                )
            
            with col_status:
                if st.session_state.is_researching:
                    st.info("🔄 正在进行深度研究，请稍候...")
        
        # 处理用户输入
        if submit_button and user_input.strip():
            # 添加用户消息到历史
            st.session_state.messages.append({
                "role": "user",
                "content": user_input
            })
            
            # 显示用户输入
            display_message(user_input, is_user=True)
            
            # 设置研究状态
            st.session_state.is_researching = True
            
            # 显示研究进度
            st.markdown("### 🔍 研究进展")
            
            # 添加进度条
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 运行研究
            try:
                # 创建进度显示容器
                progress_container = st.empty()
                
                status_text.text("正在初始化研究...")
                progress_bar.progress(10)
                
                # 运行研究
                result = run_research_sync(user_input, max_steps, progress_container)
                
                progress_bar.progress(100)
                status_text.text("研究完成！")
                
                if result:
                    # 添加助手回复到历史
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result
                    })
                    
                    # 更新研究历史
                    st.session_state.research_history.append({
                        "query": user_input,
                        "response": result
                    })
                    
                    st.success("✅ 研究完成！")
                    
                    # 清除进度显示
                    time.sleep(1)
                    progress_bar.empty()
                    status_text.empty()
                    
            except Exception as e:
                st.error(f"研究过程中出现错误: {str(e)}")
                progress_bar.empty()
                status_text.empty()
            
            finally:
                # 重置研究状态
                st.session_state.is_researching = False
                st.rerun()
    
    with col2:
        # 右侧信息面板
        st.subheader("📊 研究统计")
        
        # 显示统计信息
        total_conversations = len([msg for msg in st.session_state.messages if msg["role"] == "user"])
        total_research_sessions = len(st.session_state.research_history)
        
        st.metric("对话轮次", total_conversations)
        st.metric("研究会话", total_research_sessions)
        
        if st.session_state.research_history:
            st.markdown("### 📝 最近研究")
            for i, session in enumerate(st.session_state.research_history[-3:], 1):
                with st.expander(f"研究 {i}: {session['query'][:30]}..."):
                    st.markdown(f"**问题**: {session['query']}")
                    st.markdown("**结果**: 点击展开查看详细内容")

if __name__ == "__main__":
    main()
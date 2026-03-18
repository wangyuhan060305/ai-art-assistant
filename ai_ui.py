# 注入自定义 CSS 动效
import streamlit as st
from openai import OpenAI

st.markdown("""
    <style>
    /* 定义渐入动画 */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    # 主体内容应用动画
    .main .block-container {
        animation: fadeInUp 1s ease-out;
    }
    
    # 聊天消息平滑出现
    .stChatMessage {
        animation: fadeInUp 0.5s ease-in-out;
    }
    /* 1. 定制输入框的外观 */
    div[data-testid="stChatInput"] {
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); /* 增加回弹感的过渡 */
        border-radius: 15px;
        border: 1px solid rgba(212, 175, 55, 0.2); /* 默认淡淡的金色边框 */
    }

    /* 2. 当用户选中输入框时的“动效反馈” */
    div[data-testid="stChatInput"]:focus-within {
        transform: scale(1.02); /* 整体轻微放大 */
        border-color: #D4AF37 !important; /* 边框变亮金色 */
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.4); /* 增加金色呼吸灯光晕 */
    }

    /* 3. 让输入框内的文字光标也带上颜色 */
    textarea {
        caret-color: #D4AF37 !important;
    }
    /* 按钮悬停动效 */
    .stButton>button {
        transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
    }

    .stButton>button:hover {
        transform: translateY(-3px); /* 向上轻微浮起 */
        box-shadow: 0 5px 15px rgba(212, 175, 55, 0.3); /* 金色阴影 */
        border-color: #D4AF37 !important;
        color: #D4AF37 !important;
    }
    [data-testid="stSidebar"] {
        background-color: rgba(45, 45, 48, 0.8) !important;
        backdrop-filter: blur(10px); /* 毛玻璃模糊 */
    }
    </style>
""", unsafe_allow_html=True)

# ================= 1. 核心配置（不可在网页修改） =================
# 填入你的 DeepSeek API Key
# 从云端“保险柜”里读取 Key，而不是写死在代码里
MY_API_KEY = st.secrets["MY_DEEPSEEK_KEY"]
MY_BASE_URL = "https://api.deepseek.com"
# 固定领域：艺术设计
TARGET_DOMAIN = "艺术设计"
# AI 名字
AI_NAME = "北京化工大学艺术助手"

# ================= 2. 页面样式设置 =================
st.set_page_config(page_title=AI_NAME, page_icon="🎨")
st.title(f"🎨 {AI_NAME}")
st.caption(f"欢迎！我是您的专属助手，我只专注于【{TARGET_DOMAIN}】领域的深度交流。")

# 侧边栏改为显示固定信息，而不是输入框
with st.sidebar:
    st.header("关于助手")
    st.info(f"📍 专注领域：{TARGET_DOMAIN}")
    st.write("欢迎使用北化艺术设计学院专属 AI 助手。")
    if st.button("清空对话记录"):
        st.session_state.messages = []
        st.rerun()

# ================= 3. 限制逻辑（System Prompt） =================
SYSTEM_PROMPT = f"""
你是一个专业的【{TARGET_DOMAIN}】AI助手。
你的名字叫“{AI_NAME}”。
规则如下：
1. 你只能回答关于艺术、工业设计、视觉传达、绘画技巧、设计史、色彩理论等与{TARGET_DOMAIN}相关的问题。
2. 如果用户的问题不属于艺术设计领域（如政治、数学、日常闲聊、写代码等），你必须礼貌地拒绝。
3. 你拒绝的台词是：“抱歉，作为您的{AI_NAME}，我只能为您解答艺术设计相关的问题。”
4. 你的语气要优雅、专业且具有启发性。
"""

# ================= 4. 聊天逻辑 =================
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 接收用户输入
if prompt := st.chat_input("请描述您的艺术设计问题..."):
    # 保存用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 调用 API
    try:
        client = OpenAI(api_key=MY_API_KEY, base_url=MY_BASE_URL)
        
        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *st.session_state.messages
                ],
                temperature=0.3, # 低随机性，确保严谨
            )
            answer = response.choices[0].message.content
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
    except Exception as e:
        st.error(f"发生了一点小意外：{e}")

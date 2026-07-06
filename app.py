import json
import os
import sys
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from media_matrix.agents.publisher_agent import PublisherAgent
from media_matrix.agents.trend_agent import TrendAgent
from media_matrix.agents.writer_agent import WriterAgent
from media_matrix.state import PublisherOutput, State


st.set_page_config(
    page_title="AI 自媒体矩阵全自动运营官",
    page_icon="🤖",
    layout="wide",
)


def inject_page_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #f4efea;
            --panel: rgba(255, 253, 249, 0.88);
            --ink: #2f332f;
            --muted: #687166;
            --green: #8a9a86;
            --green-dark: #5f6f5b;
            --line: rgba(95, 111, 91, 0.18);
            --warm: #a1785a;
            --rose: #c58f7b;
        }

        .stApp {
            background:
                radial-gradient(circle at 10% 10%, rgba(138, 154, 134, 0.18), transparent 28%),
                radial-gradient(circle at 88% 6%, rgba(197, 143, 123, 0.16), transparent 24%),
                linear-gradient(135deg, #f4efea 0%, #fbf8f3 48%, #eef2ea 100%);
            color: var(--ink);
        }

        .block-container {
            max-width: 1180px;
            padding-top: 2.2rem;
            padding-bottom: 4rem;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #fffdf9 0%, #f0ebe3 100%);
            border-right: 1px solid var(--line);
        }

        .hero-shell {
            padding: 28px 30px;
            border: 1px solid rgba(255, 255, 255, 0.72);
            border-radius: 28px;
            background: rgba(255, 253, 249, 0.76);
            box-shadow: 0 24px 80px rgba(72, 59, 45, 0.12);
            backdrop-filter: blur(18px);
            margin-bottom: 26px;
        }

        .hero-kicker {
            color: var(--green-dark);
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 0;
            margin-bottom: 8px;
        }

        .hero-title {
            color: var(--ink);
            font-size: clamp(34px, 5vw, 58px);
            line-height: 1.08;
            font-weight: 800;
            letter-spacing: 0;
            margin: 0;
        }

        .hero-subtitle {
            max-width: 780px;
            color: var(--muted);
            font-size: 17px;
            line-height: 1.75;
            margin-top: 14px;
            margin-bottom: 0;
        }

        .agent-rail {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 22px;
        }

        .agent-chip {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 9px 13px;
            border: 1px solid var(--line);
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.58);
            color: var(--green-dark);
            font-size: 14px;
            font-weight: 650;
        }

        .stTextInput input {
            border-radius: 16px;
            border: 1px solid var(--line);
            background: rgba(255, 253, 249, 0.9);
            min-height: 50px;
        }

        .stButton button {
            min-height: 50px;
            border-radius: 16px;
            border: 0;
            background: linear-gradient(135deg, var(--green-dark), var(--green));
            box-shadow: 0 16px 36px rgba(95, 111, 91, 0.28);
            font-weight: 800;
        }

        [data-testid="stChatMessage"] {
            border-radius: 22px;
            border: 1px solid rgba(255, 255, 255, 0.72);
            background: rgba(255, 253, 249, 0.82);
            box-shadow: 0 18px 46px rgba(72, 59, 45, 0.09);
        }

        [data-testid="stChatMessage"] p {
            color: var(--ink);
            font-size: 16px;
            line-height: 1.68;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            border-bottom: 1px solid var(--line);
        }

        .stTabs [data-baseweb="tab"] {
            height: 48px;
            border-radius: 14px 14px 0 0;
            color: var(--muted);
            font-weight: 700;
        }

        .stTabs [aria-selected="true"] {
            background: rgba(255, 253, 249, 0.88);
            color: var(--green-dark);
        }

        .result-card {
            border: 1px solid rgba(255, 255, 255, 0.76);
            border-radius: 24px;
            background: rgba(255, 253, 249, 0.86);
            box-shadow: 0 24px 70px rgba(72, 59, 45, 0.12);
            padding: 24px;
            margin-top: 18px;
        }

        .xhs-preview {
            border-radius: 22px;
            border: 1px solid rgba(197, 143, 123, 0.28);
            background: linear-gradient(180deg, #fffdf9 0%, #fbf1ee 100%);
            padding: 22px;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.85);
        }

        .section-label {
            color: var(--green-dark);
            font-size: 14px;
            font-weight: 800;
            margin: 0 0 12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
        <section class="hero-shell">
            <div class="hero-kicker">MULTI-AGENT CONTENT COMMAND CENTER</div>
            <h1 class="hero-title">AI 自媒体矩阵全自动运营官</h1>
            <p class="hero-subtitle">
                让 TrendAgent、WriterAgent、PublisherAgent 像一个成熟内容中台一样接力：
                先拆爆款视角，再生成多平台文案，最后完成合规审查与高级排版。
            </p>
            <div class="agent-rail">
                <span class="agent-chip">🕵️ TrendAgent · 趋势洞察</span>
                <span class="agent-chip">✍️ WriterAgent · 爆款文案</span>
                <span class="agent-chip">🛡️ PublisherAgent · 风控排版</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_phone_preview(wechat_html: str) -> str:
    return f"""
    <style>
    body {{
        margin: 0;
        background:
            radial-gradient(circle at 18% 0%, rgba(138, 154, 134, 0.22), transparent 28%),
            linear-gradient(135deg, #f4efea 0%, #fffdf9 100%);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    .preview-stage {{
        min-height: 720px;
        padding: 34px 18px;
        display: flex;
        justify-content: center;
        align-items: flex-start;
        box-sizing: border-box;
    }}
    .phone-frame {{
        width: min(430px, 100%);
        height: 680px;
        border-radius: 34px;
        padding: 14px;
        background: linear-gradient(145deg, #2f332f 0%, #5f6f5b 100%);
        box-shadow: 0 30px 80px rgba(47, 51, 47, 0.28);
        box-sizing: border-box;
    }}
    .phone-screen {{
        height: 100%;
        overflow: auto;
        border-radius: 24px;
        background: #fffdf9;
        box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.82);
    }}
    .phone-topbar {{
        position: sticky;
        top: 0;
        z-index: 10;
        padding: 14px 18px 12px;
        background: rgba(255, 253, 249, 0.94);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(138, 154, 134, 0.18);
        color: #5f6f5b;
        font-size: 13px;
        font-weight: 700;
    }}
    .article-body {{
        padding: 18px 16px 28px;
        box-sizing: border-box;
    }}
    </style>
    <main class="preview-stage">
        <section class="phone-frame">
            <section class="phone-screen">
                <div class="phone-topbar">微信公众号 · 高级排版预览</div>
                <article class="article-body">
                    {wechat_html}
                </article>
            </section>
        </section>
    </main>
    """


def render_trend_json(state: State) -> None:
    if state.trend_result is None:
        st.error("TrendAgent 未返回趋势数据。")
        return

    with st.expander("查看爆款切入视角与痛点分析"):
        st.code(
            json.dumps(state.trend_result.model_dump(), ensure_ascii=False, indent=2),
            language="json",
        )


def run_pipeline_with_chat(topic: str) -> State:
    state = State()
    state.topic = topic

    with st.chat_message("assistant", avatar="🕵️"):
        st.markdown("**TrendAgent 接棒。** 我先拆解真实痛点、爆款切入角度和可延展关键词。")
        with st.spinner("趋势雷达扫描中..."):
            state = TrendAgent().run(state)
        if state.trend_result:
            st.markdown("趋势分析完成，我把高点击动机和内容入口整理好了，交给 WriterAgent。")
        else:
            st.error("趋势分析失败，流水线已中止。")
        render_trend_json(state)

    if "failed" in state.current_step:
        return state

    with st.chat_message("assistant", avatar="✍️"):
        st.markdown("**WriterAgent 收到。** 我会把趋势洞察拆成小红书和公众号两套表达。")
        with st.spinner("多平台文案生成中..."):
            state = WriterAgent().run(state)
        if state.content_result:
            st.markdown("文案生成完成：小红书负责抓眼球，公众号负责讲深度。现在交给 PublisherAgent 做最后精修。")
        else:
            st.error("文案生成失败，流水线已中止。")

    if "failed" in state.current_step:
        return state

    with st.chat_message("assistant", avatar="🛡️"):
        st.markdown("**PublisherAgent 上线。** 我会先做风险词审查，再把微信稿升级为莫兰迪风格高级排版。")
        with st.spinner("合规审查与排版生成中..."):
            state = PublisherAgent().run(state)
        publish_result = state.publish_result
        if publish_result and publish_result.is_safe:
            st.markdown("审查通过，最终发布稿已就绪。下面进入成果预览区。")
        elif publish_result:
            st.error(f"需要人工复核：{publish_result.risk_reason}")
        else:
            st.error("排版发布结果为空，请检查 Agent 输出。")

    return state


def render_results(publish_result: PublisherOutput | None) -> None:
    st.markdown("### 最终成果")

    if publish_result is None:
        st.error("发布结果为空，请检查 Agent 输出。")
        return

    if not publish_result.is_safe:
        st.error(f"风险提示：{publish_result.risk_reason}")
        return

    xhs_tab, wechat_tab = st.tabs(["📷 小红书全矩阵效果", "🟢 微信公众号高级排版"])

    with xhs_tab:
        st.markdown(
            """
            <section class="result-card">
                <p class="section-label">XIAOHONGSHU DISTRIBUTION COPY</p>
                <div class="xhs-preview">
            """,
            unsafe_allow_html=True,
        )
        st.markdown(publish_result.xiaohongshu_markdown)
        st.markdown("</div></section>", unsafe_allow_html=True)
        with st.expander("查看小红书 Markdown 源代码"):
            st.text_area(
                "小红书 Markdown",
                value=publish_result.xiaohongshu_markdown,
                height=280,
                label_visibility="collapsed",
            )

    with wechat_tab:
        st.markdown(
            """
            <section class="result-card">
                <p class="section-label">WECHAT ARTICLE MOBILE PREVIEW</p>
            </section>
            """,
            unsafe_allow_html=True,
        )
        components.html(
            render_phone_preview(publish_result.wechat_html),
            height=760,
            scrolling=False,
        )
        with st.expander("查看微信公众号 HTML 源代码"):
            st.text_area(
                "微信公众号 HTML",
                value=publish_result.wechat_html,
                height=320,
                label_visibility="collapsed",
            )


inject_page_style()
render_hero()

with st.sidebar:
    st.header("⚙️ 引擎配置")
    api_key = st.text_input(
        "DeepSeek API Key",
        value=os.getenv("DEEPSEEK_API_KEY", ""),
        type="password",
    )
    if api_key:
        os.environ["DEEPSEEK_API_KEY"] = api_key

    st.divider()
    st.caption("输出会按聊天交接形式实时展示，最终稿收纳到双 Tab 预览区。")

topic = st.text_input(
    "💡 输入原始自媒体选题",
    placeholder="例如：大模型时代的 Vibe Coding，应届生如何降维打击传统程序员？",
)

if st.button("🚀 启动多 Agent 协同生成", type="primary", use_container_width=True):
    if not os.getenv("DEEPSEEK_API_KEY"):
        st.error("请在侧边栏配置 DeepSeek API Key。")
    elif not topic.strip():
        st.warning("选题不能为空。")
    else:
        final_state = run_pipeline_with_chat(topic.strip())
        if final_state.publish_result and final_state.current_step == "publish_formatted":
            st.success("🎉 自媒体全管道流转成功。")
        render_results(final_state.publish_result)

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from media_matrix.main import DEFAULT_TOPIC, run_pipeline  # noqa: E402

st.set_page_config(page_title="自媒体矩阵运营官", page_icon="🚀", layout="wide")
st.title("自媒体矩阵全自动运营官")
topic = st.text_area("选题", DEFAULT_TOPIC, height=90)

if st.button("生成发布稿", type="primary", use_container_width=True):
    with st.spinner("Agent 正在分析趋势、撰写文案、格式化发布稿..."):
        state = run_pipeline(topic.strip())
    st.caption(f"当前状态：{state.current_step} | 审核：{state.review_status}")

    if state.trend_result:
        st.subheader("趋势分析")
        st.json(state.trend_result.model_dump(), expanded=False)
    if state.content_result:
        left, right = st.columns(2)
        with left:
            st.subheader("小红书")
            st.markdown(f"### {state.content_result.xiaohongshu_title}")
            st.write(state.content_result.xiaohongshu_content)
        with right:
            st.subheader("公众号")
            st.markdown(f"### {state.content_result.wechat_title}")
            st.write(state.content_result.wechat_content)
    publisher_result = getattr(state, "publisher_result", None) or getattr(state, "publish_result", None)
    if publisher_result:
        st.subheader("发布稿")
        st.info("合规通过" if publisher_result.is_safe else publisher_result.risk_reason)
        st.markdown(publisher_result.xiaohongshu_markdown)
        with st.expander("公众号 HTML"):
            st.code(publisher_result.wechat_html, language="html")

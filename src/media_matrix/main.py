import os
import sys

from media_matrix.agents.trend_agent import TrendAgent
from media_matrix.agents.publisher_agent import PublisherAgent
from media_matrix.agents.writer_agent import WriterAgent
from media_matrix.state import State

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

START_ICON = "\U0001f680"
ARROW_ICON = "\u2794"
CHECK_ICON = "\u2713"
ERROR_ICON = "\u274c"
PARTY_ICON = "\U0001f389"

DEFAULT_TOPIC = (
    "\u5927\u6a21\u578b\u65f6\u4ee3\u7684 Vibe Coding\uff0c"
    "\u5e94\u5c4a\u751f\u5982\u4f55\u964d\u7ef4\u6253\u51fb"
    "\u4f20\u7edf\u7a0b\u5e8f\u5458\uff1f"
)


def run_pipeline(topic: str) -> State:
    print(f"{START_ICON} \u542f\u52a8\u81ea\u5a92\u4f53\u77e9\u9635 Agent \u7ba1\u9053\uff0c\u539f\u59cb\u9009\u9898: '{topic}'\n")

    state = State()
    state.topic = topic

    pipeline = [
        TrendAgent(),
        WriterAgent(),
        PublisherAgent(),
    ]

    for agent in pipeline:
        print(f"{ARROW_ICON} \u6b63\u5728\u6d41\u7ecf Agent: {agent.name}...")
        state = agent.run(state)
        print(f"{CHECK_ICON} \u5f53\u524d\u7ba1\u9053\u72b6\u6001: {state.current_step}\n")

        if "failed" in state.current_step:
            print(f"{ERROR_ICON} \u7ba1\u9053\u5728 {agent.name} \u5904\u4e2d\u65ad\u3002")
            return state

    print(f"====== {PARTY_ICON} \u5168\u81ea\u52a8\u5316\u5185\u5bb9\u77e9\u9635\u751f\u6210\u6210\u529f {PARTY_ICON} ======")
    print(f"\n\u30101. \u8d8b\u52bf\u5206\u6790\u89c6\u89d2\u3011:\n{state.trend_result}")

    if state.content_result is None:
        print("\n\u6587\u6848\u751f\u6210\u7ed3\u679c\u4e3a\u7a7a\u3002")
        return state

    print(
        "\n\u30102. \u5c0f\u7ea2\u4e66\u7206\u6b3e\u6587\u6848\u3011:\n"
        f"\u6807\u9898: {state.content_result.xiaohongshu_title}\n"
        f"\u6b63\u6587:\n{state.content_result.xiaohongshu_content}"
    )
    print(
        "\n\u30103. \u5fae\u4fe1\u516c\u4f17\u53f7\u6df1\u5ea6\u6587\u6848\u3011:\n"
        f"\u6807\u9898: {state.content_result.wechat_title}\n"
        f"\u6b63\u6587:\n{state.content_result.wechat_content}"
    )
    publisher_result = getattr(state, "publisher_result", None) or getattr(state, "publish_result", None)
    if publisher_result is not None:
        print(
            "\n【4. 格式化发布稿】:\n"
            f"是否安全: {publisher_result.is_safe}\n"
            f"风险原因: {publisher_result.risk_reason}\n"
            f"小红书 Markdown:\n{publisher_result.xiaohongshu_markdown}\n"
            f"公众号 HTML:\n{publisher_result.wechat_html}"
        )

    return state


if __name__ == "__main__":
    # os.environ["DEEPSEEK_API_KEY"] = "your-key"
    run_pipeline(DEFAULT_TOPIC)

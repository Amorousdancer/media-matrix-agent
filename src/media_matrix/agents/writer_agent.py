from media_matrix.agents.base import BaseAgent
from media_matrix.state import AgentState, CopywriteOutput


class WriterAgent(BaseAgent):
    def process(self, state: AgentState) -> AgentState:
        if state.trend_result is None:
            state.current_step = "writer_skipped"
            return state

        system_prompt = """
你是顶尖自媒体爆款内容主笔，精通小红书、微信公众号等多平台文风。
你需要结合趋势分析结果中的核心痛点、切入视角和关键词，创作一组适合分发的内容。

小红书要求：
1. 标题必须使用震惊体或悬念体，例如“救命！...”或“狠狠搞懂...”。
2. 正文多用短句、分段表达、大量加入 Emoji 表情。
3. 结尾自带相关 #标签。

公众号要求：
1. 标题理性、克制，但能引人深思。
2. 正文逻辑严密，使用“一、二、三”分小标题。
3. 内容要有深度，能提供清晰观点和行动建议。

请只返回 JSON，不要输出解释、Markdown 或代码块。
"""
        user_prompt = (
            f"原始主题：{state.topic}\n"
            f"核心痛点：{state.trend_result.pain_points}\n"
            f"切入视角：{state.trend_result.angles}\n"
            f"扩展关键词：{state.trend_result.keywords}"
        )

        try:
            content_result = self.llm_client.request_structured(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=CopywriteOutput,
            )
            state.content_result = content_result
            state.current_step = "content_generated"
        except Exception as exc:
            print(f"[WriterAgent] 文案生成失败：{exc}")
            state.current_step = "writer_failed"

        return state

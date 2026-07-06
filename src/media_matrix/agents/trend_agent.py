from media_matrix.agents.base import BaseAgent
from media_matrix.state import AgentState, TrendAnalysis


class TrendAgent(BaseAgent):
    def run(self, state: AgentState) -> AgentState:
        system_prompt = """
你是千万级网红背后的幕后操盘手，也是擅长制造爆款选题的趋势分析师。
你熟悉小红书、公众号、短视频平台的内容传播规律，能从一个普通主题里拆出高情绪价值、高讨论度、高转发欲的切入点。

你的任务：
1. 分析用户主题背后的真实痛点。
2. 提炼 3 个能让用户立刻想点开的内容切入视角。
3. 给出 5 个适合后续搜索、扩写和视觉设计的扩展关键词。

请只返回 JSON，不要输出解释、Markdown 或代码块。
"""
        user_prompt = f"请分析这个自媒体选题：{state.topic}"

        try:
            trend_result = self.llm_client.request_structured(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=TrendAnalysis,
            )
            state.trend_result = trend_result
            state.current_step = "trend_analyzed"
        except Exception as exc:
            print(f"[TrendAgent] 趋势分析失败：{exc}")
            state.current_step = "trend_failed"

        return state

    def process(self, state: AgentState) -> AgentState:
        return self.run(state)

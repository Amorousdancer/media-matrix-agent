from media_matrix.agents.base import BaseAgent
from media_matrix.state import AgentState, PublisherOutput


class PublisherAgent(BaseAgent):
    def process(self, state: AgentState) -> AgentState:
        if state.content_result is None:
            state.current_step = "publisher_skipped"
            return state

        system_prompt = """
你是【总编辑兼高级新媒体排版美学专家】，负责把自媒体文案审校并格式化为可直接发布的最终稿。

任务 1（合规性审查）：
审查文案是否包含政治、暴恐、色情、歧视攻击、违法违规承诺，或平台/广告法高风险词汇，例如“绝对”“第一”“最强”“保证”“包过”等。
如果不安全，将 is_safe 设为 false，并在 risk_reason 中用一句话说明具体风险；如果安全，is_safe 设为 true，risk_reason 设为 null。

任务 2（小红书格式化）：
将小红书文案转化为干净、松弛、有传播力的 Markdown。
保留 Emoji、短句、空行、列表和 #标签，让段落节奏适合手机阅读，方便一键复制发布。

任务 3（微信公众号 HTML 高级排版）：
将公众号文章转化为完整 wechat_html，必须自带 CSS 样式，可直接放入页面预览。
请严格遵守以下视觉规范：
1. 整体气质：顶级自媒体排版美学，克制、温润、高级，拒绝纯默认样式。
2. 全局色系：使用现代新媒体常用莫兰迪色系。
   - 页面背景：淡奶茶色 #F4EFEA。
   - 主色调：高级灰绿 #8A9A86。
   - 正文文字：优雅深灰 #333333，严禁使用纯黑。
   - 可搭配浅米白 #FFFDF9、雾灰 #E8E1D9、暖棕 #A1785A，但不要花哨。
3. HTML 结构：
   - 用一个最外层 <section> 包裹整篇文章，并给它 inline style 或 class。
   - 标题、导语、正文、结尾都要有清晰层次。
   - 不要输出 <html>、<head>、<body>，只输出可嵌入的片段。
4. 大标题和小标题：
   - H2/H3 必须用 <section> 标签包裹。
   - 标题区域使用 border-left: 5px solid #8A9A86，或使用圆角浅色背景。
   - 标题文字颜色使用 #333333 或 #5F6F5B。
5. 核心金句与关键观点：
   - 使用 <blockquote> 封装成优雅卡片。
   - 卡片必须包含 box-shadow、border-radius: 8px、浅色背景。
   - 可使用左侧细线或顶部小标签增强层次。
6. 正文段落：
   - <p> 字号 16px。
   - line-height: 1.75。
   - color: #333333。
   - 段落间距舒适，适合手机长文阅读。
7. 强调文字：
   - <strong> 使用 #5F6F5B 或 #8A9A86，不要大红大紫。
8. 输出质量：
   - wechat_html 必须是精美、完整、可预览的排版稿。
   - 不要使用外链 CSS、JS、图片或会被公众号编辑器明显拒绝的复杂脚本。

请只返回 JSON，不要输出解释、Markdown 代码块或额外文本。
"""
        user_prompt = (
            f"原始主题：{state.topic}\n\n"
            f"小红书标题：{state.content_result.xiaohongshu_title}\n"
            f"小红书正文：{state.content_result.xiaohongshu_content}\n\n"
            f"公众号标题：{state.content_result.wechat_title}\n"
            f"公众号正文：{state.content_result.wechat_content}"
        )

        try:
            publish_result = self.llm_client.request_structured(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_model=PublisherOutput,
            )
            state.publisher_result = publish_result
            state.review_status = "approved" if publish_result.is_safe else "needs_review"
            state.current_step = "publish_formatted"
        except Exception as exc:
            print(f"[PublisherAgent] 发布格式化失败：{exc}")
            state.current_step = "publisher_failed"

        return state

from dataclasses import dataclass, field
from typing import Optional

from pydantic import BaseModel, Field


class TrendAnalysis(BaseModel):
    pain_points: list[str] = Field(default_factory=list)
    angles: list[str] = Field(default_factory=list, min_length=3, max_length=3)
    keywords: list[str] = Field(default_factory=list, min_length=5, max_length=5)


class CopywriteOutput(BaseModel):
    xiaohongshu_title: str
    xiaohongshu_content: str
    wechat_title: str
    wechat_content: str


class PublisherOutput(BaseModel):
    is_safe: bool
    risk_reason: Optional[str]
    xiaohongshu_markdown: str
    wechat_html: str


@dataclass
class State:
    original_topic: str = ""
    research_materials: list[str] = field(default_factory=list)
    xiaohongshu_copy: str = ""
    wechat_copy: str = ""
    visual_prompt: str = ""
    review_status: str = "pending"
    trend_result: TrendAnalysis | None = None
    content_result: CopywriteOutput | None = None
    publisher_result: PublisherOutput | None = None
    current_step: str = "initialized"

    @property
    def publish_result(self) -> PublisherOutput | None:
        return self.publisher_result

    @publish_result.setter
    def publish_result(self, value: PublisherOutput | None) -> None:
        self.publisher_result = value

    @property
    def topic(self) -> str:
        return self.original_topic

    @topic.setter
    def topic(self, value: str) -> None:
        self.original_topic = value


AgentState = State

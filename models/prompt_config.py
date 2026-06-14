from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime


class PromptConfig(Document):
    key: Indexed(str, unique=True)
    title: str
    content: str
    description: str = ""
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: str | None = None

    class Settings:
        name = "prompt_configs"

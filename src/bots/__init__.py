"""A list of bots, register them at the container's registry"""
from .base import Bot
from .basic_bot import BasicBot
from .viral_bot import ViralBot
from .news_bot import NewsBot
from .response_bot import ResponseBot

__all__ = [
    "Bot",
    "BasicBot",
    "ViralBot",
    "NewsBot",
    "ResponseBot",
]
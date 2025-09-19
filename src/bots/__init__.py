"""A list of bots, register them at the container's registry"""
from .base import Bot
from .basic_bot import BasicBot

__all__ = [
    "Bot",
    "BasicBot",
]
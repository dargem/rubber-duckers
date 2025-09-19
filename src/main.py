"""The entry point for rubber-duckers bot."""

import asyncio
import logging
from langchain.schema import HumanMessage
import time
import random
from src.config import Container, load_config
from src.providers import LLMProvider
from src.bots import BasicBot, Bot
from src.tweeter import TweeterClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_container() -> Container:
    """Initialize the dependency injection container."""
    try:
        # Load configuration
        config = load_config()
        logger.info(f"Loaded config for environment: {config.environment}")
        
        # Set log level from config
        logging.getLogger().setLevel(getattr(logging, config.log_level))
        
        # Initialize container
        container = Container()
        await container.set_config(config)
        
        logger.info("Container initialized successfully")
        return container
        
    except Exception as e:
        logger.error(f"Failed to setup container: {e}")
        logger.info("Creating example config file...")
        raise


async def test_llm_integration(container: Container) -> None:
    """Test the LLM integration with key rotation."""
    logger.info("Testing LLM integration...")
    
    try:
        # Get the LLM provider (will be the appropriate one based on config)
        llm_provider = container.get(LLMProvider)
        
        # Check health
        is_healthy = await llm_provider.health_check()
        logger.info(f"LLM provider health: {is_healthy}")
        
        if not is_healthy:
            logger.error("LLM provider is not healthy")
            return
        
        # Test a simple invocation
        test_messages = [HumanMessage(content="Say hello in exactly 5 words.")]
        response = await llm_provider.invoke(test_messages)
        logger.info(f"LLM response: {response}")
        
        # Get stats
        stats = await container.get_stats()
        logger.info(f"Container stats: {stats}")
        
    except Exception as e:
        logger.error(f"LLM integration test failed: {e}")
        raise


async def run_bot():
    """Main bot entry point."""
    logger.info("Starting bot...")
    
    try:
        # Setup dependency injection
        container = await setup_container()
        # Test the core LLM functionality
        print("testing integration")
        await test_llm_integration(container)
        print("llm tested")
        
        logger.info("Bot setup complete")

        bot:Bot = container.get(BasicBot)
        print("bot gotten")
        tweeter: TweeterClient = container.get(TweeterClient)
        print("tweet client got")
        while True:
            try:
                propaganda = await bot.run_bot()
                print(propaganda)
                tweeter.make_post(propaganda)
                print("post made")
                time.sleep(60+random.randrange(-20,20))
            except:
                time.sleep(20)
        
    except Exception as e:
        logger.error(f"Bot startup failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(run_bot())
"""The entry point for rubber-duckers bot."""

import asyncio
import logging
from langchain.schema import HumanMessage
import time
import random
from src.config import get_container, load_config
from src.providers import LLMProvider
from src.bots import BasicBot, Bot, ViralBot, NewsBot, ResponseBot
from src.tweeter import TweeterClient, QueryAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_container():
    """Initialize the dependency injection container."""
    try:
        # Load configuration
        config = load_config()
        logger.info(f"Loaded config for environment: {config.environment}")
        
        # Set log level from config
        logging.getLogger().setLevel(getattr(logging, config.log_level))
        
        # Initialize container (lazy load to avoid circular imports)
        Container = get_container()
        container = Container()
        await container.set_config(config)
        
        logger.info("Container initialized successfully")
        return container
        
    except Exception as e:
        logger.error(f"Failed to setup container: {e}")
        logger.info("Creating example config file...")
        raise


async def test_llm_integration(container) -> None:
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

        basic_bot:Bot = container.get(BasicBot)
        viral_bot:Bot = container.get(ViralBot)
        news_bot:Bot = container.get(NewsBot)
        response_bot:Bot = container.get(ResponseBot)
        logger.info("Bot instance created successfully")
        tweeter: TweeterClient = container.get(TweeterClient)
        logger.info("TweeterClient instance created successfully")

        post_count = 0
        while True:
            try:
                rand = random.randint(0,2)
                if rand == 0:
                    print("running normal")
                    bot = basic_bot
                elif rand == 1:
                    print("running viral")
                    bot = viral_bot
                else:
                    print("running news bot")
                    bot = news_bot

                
                post_count += 1
                logger.info(f"Starting post generation #{post_count}")
                
                propaganda = await bot.run_bot()
                logger.info(f"Content generated ({len(propaganda)} chars)")
                
                post_id = await tweeter.make_post(propaganda)
                logger.info(f"Post #{post_count} successful! Post ID: {post_id}")

                for i in range(2):
                    sleep_time = 50 + random.randrange(-20, 20)
                    logger.info(f"Sleeping for {sleep_time} seconds until next reply...")
                    time.sleep(sleep_time)
                    print("making a reply")

                    while True:
                        try:
                            response = await response_bot.run_bot(propaganda)
                            await tweeter.send_reply(reply=response, post_id=post_id)
                            break
                        except:
                            print("response failed, sleeping 10s")
                            time.sleep(10)

                    print("reply made")

                sleep_time = 50 + random.randrange(-20, 20)
                logger.info(f"Sleeping for {sleep_time} seconds until next post...")
                time.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Post #{post_count} failed: {e}")
                logger.info("Retrying in 20 seconds...")
                time.sleep(10)
        
    except Exception as e:
        logger.error(f"Bot startup failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(run_bot())
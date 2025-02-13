import asyncio
from vk_bot_manager import VKBotManager

async def main():
    manager = VKBotManager()
    await manager.start()

if __name__ == "__main__":
    asyncio.run(main())
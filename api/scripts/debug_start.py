
import asyncio
from app.main import app, lifespan

async def start():
    print("Starting manual lifespan...")
    try:
        async with lifespan(app):
            print("Startup successful!")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Startup failed: {e}")

if __name__ == "__main__":
    asyncio.run(start())

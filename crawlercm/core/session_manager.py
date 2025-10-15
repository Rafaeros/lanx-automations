import sys
import aiohttp
from contextlib import asynccontextmanager
from fastapi import FastAPI
from bs4 import BeautifulSoup
from core.config import settings
from core.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.

    Handles initialization and shutdown tasks:
      - Creates an aiohttp session
      - Retrieves CSRF token from login page
      - Authenticates with the target system
      - Closes session on shutdown
    """
    logger.info("Initializing aiohttp session...")
    session = aiohttp.ClientSession()

    try:
        # Step 1: Get CSRF Token
        logger.info(f"Accessing {settings.LOGIN_URL} to get CSRF token...")
        async with session.get(settings.LOGIN_URL) as response:
            response.raise_for_status()
            html_content = await response.text()

        soup = BeautifulSoup(html_content, "html.parser")
        csrf_input = soup.find("input", {"name": "YII_CSRF_TOKEN"})

        if not csrf_input or "value" not in csrf_input.attrs:
            raise IOError("Could not find CSRF token input on login page.")

        csrf_token = csrf_input["value"]
        logger.info("CSRF token extracted successfully!")

        app.state.csrf_token = csrf_token

        # Step 2: Perform login
        login_payload = {
            "YII_CSRF_TOKEN": csrf_token,
            "LoginForm[username]": settings.USERNAME,
            "LoginForm[password]": settings.PASSWORD,
            "LoginForm[codigoConexao]": "3.1~13,3^17,7",
            "yt0": "Entrar",
        }

        logger.info("Sending login request...")
        async with session.post(settings.LOGIN_URL, data=login_payload) as response:
            response.raise_for_status()
            if response.status != 200:
                raise IOError(f"Login failed: HTTP {response.status}")

        logger.info("✅ Login successful! Scraper ready.")
        app.state.http_client = session

        # Yield control to app runtime
        yield

    except (aiohttp.ClientError, IOError) as e:
        logger.exception(f"❌ Critical Error during initialization: {e}")
        await session.close()
        sys.exit("Application terminated due to authentication failure.")

    finally:
        if hasattr(app.state, "http_client") and not app.state.http_client.closed:
            await app.state.http_client.close()
            logger.warning("Aiohttp session closed gracefully.")

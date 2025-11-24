from datetime import date, datetime
import sys
from typing import List, Optional
import aiohttp
from contextlib import asynccontextmanager
from fastapi import FastAPI
from bs4 import BeautifulSoup
from core.logger import logger
from core.config_manager import Configs
from schemas.reports_schemas import SalesReportItem


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

    settings = Configs()

    try:
        # Step 1: Get CSRF Token
        logger.info(
            f"Accessing https://v2.cargamaquina.com.br/site/login/c/3.1~13,3%5e17,7 to get CSRF token..."
        )
        async with session.get(
            "https://v2.cargamaquina.com.br/site/login/c/3.1~13,3%5e17,7"
        ) as response:
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
            "LoginForm[username]": settings.username,
            "LoginForm[password]": settings.password,
            "LoginForm[codigoConexao]": "3.1~13,3^17,7",
            "yt0": "Entrar",
        }

        logger.info("Sending login request...")
        async with session.post(
            "https://v2.cargamaquina.com.br/site/login/c/3.1~13,3%5e17,7",
            data=login_payload,
        ) as response:
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


class AuthOnCM:
    def __init__(self):
        self.session: aiohttp.ClientSession | None = None
        self.csrf_token: str | None = None
        self.auth_config = Configs()
        self.base_url = ""
        self.login_code_url = ""
        self.username = self.auth_config.username
        self.password = self.auth_config.password

    async def login(self):
        self.auth_config.load()
        logger.info("Starting aiohttp session...")
        self.session = aiohttp.ClientSession()

        try:
            logger.info(f"Getting CSRF from https://lanx.cargamaquina.com.br/ ...")

            async with self.session.get(
                "https://lanx.cargamaquina.com.br/", allow_redirects=True
            ) as r:
                r.raise_for_status()
                final_url: str = str(r.url)
                self.base_url = final_url.split("/site")[0]
                self.login_code_url = final_url.split("/c/")[-1]
                html = await r.text()

            soup = BeautifulSoup(html, "html.parser")
            csrf_input = soup.find("input", {"name": "YII_CSRF_TOKEN"})

            if not csrf_input or "value" not in csrf_input.attrs:
                raise Exception("CSRF token not found.")

            self.csrf_token = csrf_input["value"]
            logger.info("CSRF token extracted.")

            login_payload = {
                "YII_CSRF_TOKEN": self.csrf_token,
                "LoginForm[username]": self.username,
                "LoginForm[password]": self.password,
                "LoginForm[codigoConexao]": f"{self.login_code_url}",
                "yt0": "Entrar",
            }

            logger.info("Sending login request...")
            async with self.session.post(
                f"{self.base_url}/site/login/c/{self.login_code_url}",
                data=login_payload,
            ) as r:
                r.raise_for_status()

            logger.info("✅ Login successful!")
            return True

        except Exception as e:
            logger.exception(f"Login failed: {e}")
            await self.close()
            return False

    async def get_client(self) -> aiohttp.ClientSession:
        if self.session and not self.session.closed:
            return self.session
        logger.warning("Session invalid or closed — re-authenticating...")
        ok = await self.login()
        if not ok:
            raise RuntimeError("Unable to create authenticated session.")

        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("Session closed.")

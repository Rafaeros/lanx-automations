import ssl
import aiohttp
import certifi
from bs4 import BeautifulSoup
from core.logger import logger
from core.config_manager import Configs


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
        logger.info("Starting aiohttp session...")
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=ssl_context),
            cookie_jar=aiohttp.CookieJar(unsafe=True),
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; aiohttp-client)"
            },
        )
        try:
            logger.info(f"Getting CSRF from https://lanx.cargamaquina.com.br/ ...")

            async with self.session.get(
                "https://lanx.cargamaquina.com.br/", allow_redirects=True
            ) as r:
                r.raise_for_status()
                final_url: str = str(r.url)
                logger.info(f"Redirecting to {final_url}...")
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

            logger.info(
                f"Sending login request to {self.base_url}/site/login/c/{self.login_code_url}..."
            )
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
        self.auth_config.load()
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

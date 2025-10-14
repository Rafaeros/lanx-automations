import aiohttp
from contextlib import asynccontextmanager
from fastapi import FastAPI
from bs4 import BeautifulSoup # <-- 1. NOVO: Importe o BeautifulSoup
from core.config import settings
import sys

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação, criando uma sessão aiohttp
    autenticada no site alvo durante a inicialização.
    """
    print("Iniciando a aplicação e a sessão aiohttp...")
    session = aiohttp.ClientSession()

    try:
        # --- ETAPA 1: Obter o CSRF Token da página de login ---
        print(f"Acessando {settings.LOGIN_URL} para obter o CSRF token...")
        async with session.get(settings.LOGIN_URL) as response:
            response.raise_for_status()
            html_content = await response.text()

        # --- ETAPA 2: Extrair o token do HTML com BeautifulSoup ---
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Encontra o input com o nome 'YII_CSRF_TOKEN'
        csrf_token_input = soup.find('input', {'name': 'YII_CSRF_TOKEN'})

        if not csrf_token_input or 'value' not in csrf_token_input.attrs:
            raise IOError("Não foi possível encontrar o input do CSRF token na página de login.")
        
        csrf_token = csrf_token_input['value']
        print("CSRF Token extraído com sucesso!")
        
        # --- ETAPA 3: Montar o payload de login com o token dinâmico ---
        login_payload = {
            'YII_CSRF_TOKEN': csrf_token, # <-- 2. MUDANÇA: Usa o token extraído
            'LoginForm[username]': settings.USERNAME,
            'LoginForm[password]': settings.PASSWORD,
            'LoginForm[codigoConexao]': '3.1~13,3^17,7',
            'yt0': 'Entrar'
        }

        # --- ETAPA 4: Enviar a requisição de login ---
        print("Enviando requisição de login...")
        async with session.post(settings.LOGIN_URL, data=login_payload) as response:
            response.raise_for_status()
            if response.status != 200:
                raise IOError("Falha no login do scraper. O status da resposta não foi 200.")
            
            print("Login do scraper realizado com sucesso!")
            app.state.http_client = session
        
        yield
        
    except (aiohttp.ClientError, IOError) as e:
        print(f"ERRO CRÍTICO: {e}")
        await session.close()
        sys.exit("Aplicação encerrada devido a falha na autenticação do scraper.")
    finally:
        if 'http_client' in app.state and not app.state.http_client.closed:
            await app.state.http_client.close()
            print("Sessão aiohttp encerrada.")
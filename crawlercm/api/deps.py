from fastapi import Request, HTTPException, status
import aiohttp

def get_authenticated_client(request: Request) -> aiohttp.ClientSession:
    """
    Função de dependência para obter a sessão aiohttp autenticada.

    Ela busca a sessão que foi criada e armazenada no 'app.state'
    pela função lifespan durante a inicialização do servidor.
    """
    if not hasattr(request.app.state, 'http_client') or request.app.state.http_client.closed:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="A sessão de scraping não está disponível ou foi encerrada."
        )
    
    return request.app.state.http_client
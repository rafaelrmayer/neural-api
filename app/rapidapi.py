"""Separate authenticated gateway paths from the existing public demo API."""
import hmac
import os

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send


GATEWAY_METHODS = {
    '/health': 'GET',
    '/v1/models': 'GET',
    '/v1/predict': 'POST',
    '/v1/cards/suggestions': 'POST',
    '/v1/cards/random-forest/suggestions': 'POST',
}


class RapidAPIGateway:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        path = scope.get('path', '')
        if scope['type'] != 'http' or not (path == '/rapidapi' or path.startswith('/rapidapi/')):
            await self.app(scope, receive, send)
            return

        target = path[len('/rapidapi'):]
        method = GATEWAY_METHODS.get(target)
        if method is None:
            response = JSONResponse({'error': 'not_found'}, status_code=404)
        elif scope['method'] != method:
            response = JSONResponse({'error': 'method_not_allowed'}, status_code=405,
                                    headers={'Allow': method})
        else:
            secret = os.environ.get('RAPIDAPI_PROXY_SECRET', '')
            supplied = [value for key, value in scope.get('headers', [])
                        if key.lower() == b'x-rapidapi-proxy-secret']
            if not secret.strip():
                response = JSONResponse({'error': 'gateway_not_configured'}, status_code=503)
            elif len(supplied) != 1 or not hmac.compare_digest(supplied[0], secret.encode('utf-8')):
                response = JSONResponse({'error': 'gateway_unauthorized'}, status_code=403)
            else:
                # Only the path changes: body streaming, query parameters and model lifecycle
                # are handled by the original FastAPI routes, with their existing contracts.
                forwarded = dict(scope, path=target, raw_path=target.encode('utf-8'))
                await self.app(forwarded, receive, send)
                return
        response.headers['Cache-Control'] = 'no-store'
        await response(scope, receive, send)

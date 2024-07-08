from fastapi import Request
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    SimpleUser,
    UnauthenticatedUser,
)


from app.auth import JwtGenerator

class CustomAuthenticationMiddleWare:
    async def authenticate(self, request: Request):
        token = request.cookies.get("token")
        user_id = JwtGenerator.get_current_user(token)
        if not user_id:
            roles = ["annon"]
            return AuthCredentials(roles), UnauthenticatedUser()
        roles = ["authenticated"]
        return AuthCredentials(roles), SimpleUser(user_id)

from datetime import datetime, timedelta
from typing import Optional

from functools import wraps
from fastapi import Depends, HTTPException, Request
import jwt
from config import Settings
from jwt.exceptions import  PyJWTError
from typing import Optional

settings = Settings()

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm



class JwtGenerator:
    @staticmethod
    def create_access_token(data: dict, expires_at: Optional[timedelta] = None) -> str:
        """
        create user access token
        """
        if  expires_at:
            expires = datetime.now() + expires_at

        else:
            expires= datetime.now() + timedelta(minutes=4)

        data.update({'exp': expires})
        return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def get_current_user(token: Optional[str] = None) -> str:
        """
        verfy the provided access token given
        """
        user_id = None
        try:
            user = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = user.get('userId')
        except PyJWTError:
            user_id = None

        return user_id


def login_required(func):
    @wraps(func)
    def wrappers(request: Request, *args, **kwargs):
        token = request.cookies.get('token') or None
        user_id = JwtGenerator().get_current_user(token)
        print(user_id)
        if not user_id:
            detail = {
                "status": "Bad request",
                "message": "Authentication failed",
                "statusCode": 401
            }
            return HTTPException(status_code=401, detail=detail)
        return func(request, *args, **kwargs)
    return wrappers
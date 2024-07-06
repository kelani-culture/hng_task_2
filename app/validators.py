import re
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from config import Settings
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

settings = Settings()

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
oauth2_password = OAuth2PasswordBearer(tokenUrl='token')
def regex_validator(pattern: str, string: str):
    return re.match(pattern, string) or None



def validate_field(field_name: str, error_msg: str = '', pattern: str = '') -> str:
    field_name_pat = regex_validator(pattern, field_name)
    if not field_name_pat:
        raise ValueError(
            f"{error_msg}"
        )

    return field_name


class JwtGenerator:
    @staticmethod
    def create_access_token(data: dict, expires_at: Optional[timedelta] = None):
        """
        create user access token
        """
        if  expires_at:
            expires_at = datetime.now(timezone.utc) + expires_at

        else:
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=4)

        data.update({'exp': expires_at})
        return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def verify_access_token(token: str):
        """
        verfy the provided access token given
        """
        user = None
        try:
            user = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except InvalidTokenError:
            user = None

        if 'userId' not in user:
            user = None
        return user
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    hash plain  text password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    verified hash password
    """
    return pwd_context.verify(plain_password, hashed_password)

post_response = {
    201: {
        "description": "Successful  registration response",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "message": "Login successful",
                    "data": {
                        "accessToken": "eyJh...",
                        "userId": "c3a77c95-0ae3-4837-90cd-e43284729c7a",
                        "first_name": "John",
                        "last_name": "Doe",
                        "email": "john.doe@example.com",
                        "password": "securepassword",
                        "phone": "000 000 000",
                    }
                }
            }
        },
    },
    400: {
        "description": "Unsuccessful registration response",
        "content": {
            "application/json": {
                "example": {
                    "status": "Bad Request",
                    "message": "User already exist",
                    "status_code": 400,
                }
            }
        },
    },
}



post_login_response = {
    200: {
        "description": "Successful  login response",
        "content": {
            "application/json": {
                "example": {
                    "status": "success",
                    "message": "Login successful",
                    "data": {
                        "accessToken": "eyJh...",
                        "userId": "c3a77c95-0ae3-4837-90cd-e43284729c7a",
                        "first_name": "John",
                        "last_name": "Doe",
                        "email": "john.doe@example.com",
                        "password": "securepassword",
                        "phone": "000 000 000",
                    }
                }
            }
        },
    },
    401: {
        "description": "Unsuccessful login response",
        "content": {
            "application/json": {
                "example": {
                    "status": "Bad Request",
                    "message": "Authentication Failed",
                    "status_code": 401,
                }
            }
        },
    },
}
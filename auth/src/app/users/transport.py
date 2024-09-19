from fastapi import status
from fastapi_users.authentication import BearerTransport
from fastapi_users.openapi import OpenAPIResponseType

from app.users.schemas import BearerResponseSchema


class RefreshableBearerTransport(BearerTransport):
    @staticmethod
    def get_openapi_login_responses_success() -> OpenAPIResponseType:
        return {
            status.HTTP_200_OK: {
                "model": BearerResponseSchema,
                "content": {
                    "application/json": {
                        "example": {
                            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1"
                            "c2VyX2lkIjoiOTIyMWZmYzktNjQwZi00MzcyLTg2Z"
                            "DMtY2U2NDJjYmE1NjAzIiwiYXVkIjoiZmFzdGFwaS"
                            "11c2VyczphdXRoIiwiZXhwIjoxNTcxNTA0MTkzfQ."
                            "M10bjOe45I5Ncu_uXvOmVV8QxnL-nZfcH96U90JaocI",
                            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1"
                            "c2VyX2lkIjoiZTZjODk4NDktYzgxYy00N2FmLWE2OTEtOTIxYTQ2MzBmZj"
                            "Q5IiwiYXVkIjpbImZhc3RhcGktdXNlcnM6YXV0aCJdLCJ0b2tlbl90eXBl"
                            "jIoicmVmcmVzaCIsImV4cCI6MTY3NDgyOTk2N30.lCZKSuHzlU__C9q9"
                            "1TFv7f8gRIAO26iu4JDUoVv9r10",
                            "token_type": "bearer",
                        }
                    }
                },
            },
        }


bearer_transport = RefreshableBearerTransport(tokenUrl="auth/jwt/login")

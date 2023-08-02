import jwt as pyjwt
from typing import Dict
from jose import JWTError, jwt as jose_jwt
from abc import ABC,abstractmethod

from utils.service_config import settings


class IToken(ABC):

    def __init__(self, token):
        self.token = token
        self.config = settings

    @abstractmethod
    def verify(self) -> Dict:
        pass


class VerifyCustomToken(IToken):

    def verify(self):
        try:
            payload = jose_jwt.decode(self.token.credentials, self.config.SECRET_KEY, algorithms=[self.config.ALGORITHM])
            return {"payload": payload, "mark": "custom_token_mark"}

        except JWTError as error:
            return {"status": "error", "msg": error.__str__()}


class VerifyAuth0Token(IToken):

    def __init__(self, token):
        super().__init__(token)
        jwks_url = f'https://{settings.DOMAIN}/.well-known/jwks.json'
        self.jwks_client = pyjwt.PyJWKClient(jwks_url)

    def verify(self) -> dict:
        try:
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(
                self.token.credentials
            ).key

        except pyjwt.exceptions.PyJWKClientError as error:
            return {"status": "error", "msg": error.__str__()}
        except pyjwt.exceptions.DecodeError as error:
            return {"status": "error", "msg": error.__str__()}

        try:
            payload = pyjwt.decode(
                self.token.credentials,
                self.signing_key,
                algorithms=settings.ALGORITHMS,
                audience=settings.API_AUDIENCE,
                issuer=settings.ISSUER,
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}

        return {"payload": payload, "mark": "auth0_mark"}
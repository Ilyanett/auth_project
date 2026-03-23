import jwt
from users.models import User, BlacklistedToken
from users.utils import decode_token


class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user_obj = None
        request.current_token = None

        auth_header = request.headers.get('Authorization', '')

        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

            try:

                if BlacklistedToken.objects.filter(token=token).exists():
                    pass
                else:
                    payload = decode_token(token)
                    request.user_obj = User.objects.filter(
                        id=payload['user_id'],
                        is_active=True
                    ).first()
                    request.current_token = token

            except jwt.ExpiredSignatureError:
                pass

            except jwt.InvalidTokenError:
                pass

        response = self.get_response(request)
        return response

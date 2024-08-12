import jwt
from django.http import JsonResponse


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        public_urls = [
            "/api/token/refresh/",
            "/login",
            "/signup",
            "/otp_verification",
            "/api/token/",
            "/favicon.ico",
            "/api/token/refresh",
            "/logout",
            "/resend_otp",
            "/forget_pass",
            "/google",
        ]

        print(request.path, "path in middleware")
        if (
            request.path in public_urls
            or request.path.startswith("/media/")
            or request.path.startswith("/ws/")
        ):
            return self.get_response(request)

        auth_header = request.headers.get("Authorization", None)
        if auth_header:
            try:
                token_type, token = auth_header.split()
                if token_type.lower() != "bearer":
                    raise ValueError("Invalid token type")
            except jwt.ExpiredSignatureError:
                return JsonResponse({"message": "Token has expired"}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({"message": "Invalid token"}, status=401)
            except ValueError as e:
                print(e, "value errorin middlewate")
                return JsonResponse({"message": str(e)}, status=401)
            except Exception as e:
                print(e, "error in middlewate extencption ")
                return JsonResponse({"message": str(e)}, status=401)
        else:
            print("no autht header")
            return JsonResponse({"message": "Authorization header missing"}, status=400)
        print("returned respponse")
        response = self.get_response(request)
        return response

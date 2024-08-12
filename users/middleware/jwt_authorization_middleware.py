import jwt
from django.http import JsonResponse
from django.conf import settings


class JWTAuthenticationMiddleware:
    """
    Middleware for JWT authentication in Django. It checks for the presence and validity of 
    JWT tokens in the Authorization header for protected routes.

    Attributes:
        get_response (callable): A callable that takes a request and returns a response.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Process the request and handle JWT authentication.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: The HTTP response object after processing the request.
        """

        # List of public URLs that do not require authentication
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
        # Skip authentication for public URLs and certain path prefixes
        if (
            request.path in public_urls
            or request.path.startswith("/media/")
            or request.path.startswith("/ws/")
        ):
            return self.get_response(request)

        auth_header = request.headers.get("Authorization", None)
        if auth_header:
            try:
                # Extract token type and token from the Authorization header
                token_type, token = auth_header.split()
                if token_type.lower() != "bearer":
                    raise ValueError("Invalid token type")
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
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

        # Proceed with the next middleware or view if authentication is successful
        response = self.get_response(request)
        return response


import jwt
from django.conf import settings
from django.http import JsonResponse
from decouple import config



class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        # public_routes = config('public_urls')
        # print(public_routes,'routes')
        public_urls = [
                    '/api/token/refresh/',
                    '/login',
                    '/signup',
                    '/otp_verification',
                    '/api/token/',
                    '/favicon.ico',
                    '/api/token/refresh',

                    
                ]
        print(request.path, 'path in middleware\n')
        if request.path in public_urls :
            print('in if and returend resopinse')
            return self.get_response(request)
        
        
        auth_header = request.headers.get('Authorization', None)
        if auth_header: 
            print('authheader in middleware\n')
            try:
                token_type, token = auth_header.split()
                print(token_type, 'token and typ e \n')
                if token_type.lower() != 'bearer':
                    raise ValueError("Invalid token type")
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                request.user_id = payload.get('user_id')
                print(request.user_id,payload,'payload and id ')
            except jwt.ExpiredSignatureError:
                return JsonResponse({'message': 'Token has expired'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'message': 'Invalid token'}, status=400)
            except ValueError as e:
                print(e,'value errorin middlewate')
                return JsonResponse({'message': str(e)}, status=401)
            except Exception as e:
                print(e,'error in middlewate extencption ')
                return JsonResponse({'message': str(e)}, status=401)
        else:
            print('no autht header')
            return JsonResponse({'message': 'Authorization header missing'}, status=400)
        print('returned respponse')
        response = self.get_response(request)
        return response

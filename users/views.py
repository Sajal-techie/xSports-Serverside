from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.validators import validate_email
from django.http import JsonResponse
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank 
from users.serializers.user_serializer import CustomUsersSerializer
from users.serializers.google_serializer import GoogleSignInSerializer
from .models import Users,Academy
from .task import send_otp
from selection_trial.models import Trial

class Signup(APIView):
    # parser_classes = (MultiPartParser,)
    def post(self, request):
        data = request.data
        
        # validations 
        errors = {}
        print('username' in data)
        if 'email' in data:
            if not data['email'] :
                print('hai hello')
                errors['email'] = "Email field is Required"
        else :
            try:
                validate_email(email)
            except:
                errors['email'] = "Email is not Valid"
       
        email = data['email']
        print(email,'\n',data)

        if 'is_academy' in data:
            if data['is_academy'] == 'true':
                data.setlist('sport', request.data.getlist('sport[]',[]))
        print(data,'sports data')

        if 'username' in data:
            if not data['username']:
                errors['username'] = "Name is required"
        if 'sport' in data:
            if not data['sport']:
                errors['sport'] = "Sport is Required"
        if 'state' in data:
            if not data['state']:
                errors['state'] = "State is required"
        if 'district' in data:
            if not data['district']:
                errors['district'] = "District is required"
        if 'dob' in data:
            if not data['dob']:
                errors['dob'] = "Date of birth is required"
        if 'password' in data:
            if not data['password']:
                errors['password'] = "Password is required"
        if 'license' in data:
            if not data['license']:
                errors['license'] = "License is required"

        print(errors,'errors')
        if Users.objects.filter(email=email).exists():
            errors['email'] = "Account with Email already exist try login"

        if errors:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'message' : errors.values()
            })
        user_serializer = CustomUsersSerializer(data=data)
        try:
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save() 
            send_otp.delay(email)
            return Response({
                'status': status.HTTP_200_OK,
                'message': 'Registration Successful, Check Email For Verification',
                
                })  
        except Exception as e:
            print(e,'exeption errorrrrr')
            return Response(e,status=status.HTTP_400_BAD_REQUEST)
 

class VerifyOtp(APIView):
    def put(self, request):
        try:
            data = request.data
            email = data['email'] if 'email' in data else None
            otp = data['otp'] if 'otp' in data else None
            user = Users.objects.get(email=email)
            print(data,otp,email,user.otp)
            if not user.otp:
                return Response({
                    'status':status.HTTP_400_BAD_REQUEST,
                    'message':"OTP Expired try resending otp"
                }) 
            if user.otp == otp:
                user.otp = None
                user.is_verified = True
                user.save()
                return Response({
                    'status': status.HTTP_200_OK,
                    'message': 'OTP Verified'
                })
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'Invalid OTP'
            }) 
        except Exception as e:
            print(e,'verify OTP error')
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message':'Your token has been expired try login again '
            })

class Login(APIView):
    def post(self, request): 
        data = request.data
        email = data['email'] if 'email' in data else None
        password = data['password'] if 'password' in data else None
        if email is None:
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message':"email field is required"
            })
        if password is None:
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message':"password field is required"
            })
        is_academy = False
        if 'is_academy' in data:
            is_academy = data['is_academy'] 
        is_staff = True if 'is_staff' in data else False
        print(data,is_academy,is_staff)
        if not Users.objects.filter(email=email).exists():
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
               'message': 'Email Does Not Exists'
            })
        user = Users.objects.get(email = email)
        print(user)
        if not user.check_password(password):
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
               'message': 'Invalid Password'
            })
        if user.is_superuser or (user.is_staff and not is_staff):
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'message':'Admin cannot loggin as user'
            })
        if is_staff and not user.is_staff:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'message':'You are not an admin '
            })
        if not user.is_active:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST, 
                'message':'You are blocked'
            })
        if user.is_academy and not is_academy:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'message': 'You are signed in as acadmey try academy login'
            })
        if not user.is_academy and is_academy:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'message': 'You are signed in as player try player login'
            })
        if not user.is_verified:
            send_otp.delay(email)
            return Response({
                'status' :status.HTTP_403_FORBIDDEN,
                'message':'You are not verified'
            })
        if is_academy:
            academy = Academy.objects.get(user=user)
            if not academy.is_certified :
                return Response({
                    'status':status.HTTP_400_BAD_REQUEST,
                    'message':'You are not approved by admin '
                })

        role = 'admin' if is_staff and user.is_staff else 'academy' if is_academy else 'player'

        return Response({
            'status': status.HTTP_200_OK,
           'message': 'Login Successful',
           'user':user.username,
           'role':role,
           'dob':user.dob
        })
    

class GoogleSignIn(GenericAPIView):
    serializer_class=GoogleSignInSerializer

    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = (serializer.validated_data)['access_token']
        print(data)
        return Response(data,status=status.HTTP_200_OK)

class Logout(APIView):
    def post(self, request):
        print(request.user,'suser')
        try:
            refresh = request.data.get('refresh')
            print(refresh,'refresh in logout',request.data)
            token = RefreshToken(refresh)
            print(token,'token in logout')
            token.blacklist()
            return Response(status=200)
        except Exception as e:
            print(e,'error in logout')
            return Response(status=400)


class ResendOtp(APIView):
    def post(self,request):
        try:
            print(request.data)
            email = request.data['email'] 
            send_otp.delay(email)
            return Response({
                'status':status.HTTP_200_OK,
                'message':"OTP sended successfully"
            })
        except Exception as e:
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'message': 'Error sending otp'
            })
    

class ForgetPassword(APIView):
    def post(self, request):
        try:
            print(request.data)
            if 'email' in request.data:
                email = request.data['email']
                if 'password' in request.data:
                    user = Users.objects.get(email=email)
                    user.set_password(request.data['password'])
                    user.save()
                    print('password changed')
                    return Response({
                        'status':status.HTTP_200_OK,
                        'message':'Password Resetted successfully'
                    })
                if Users.objects.filter(email=email).exists():
                    send_otp.delay(email)
                    print('email exist')
                    return Response({
                        'status' : status.HTTP_200_OK,
                        'message': 'Email is valid'
                    })
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': "Email is not valid, Try signin"
            })
        except Users.DoesNotExist as e:
            print(e,'does not exist')
            return Response({
                'status': status.HTTP_400_BAD_REQUEST,
                'message': 'Account does not exist'
            })

        except Exception as e:
            print(e,'error')
            return Response({
                'status':status.HTTP_400_BAD_REQUEST,
                'message': 'Internal Server Error'
            })


class SearchResult(APIView):
    def get(self,request):
        query = request.GET.get('q','')
        if query:
            players = Users.objects.filter(username__icontains=query,is_academy=False).values('username')
            academies = Users.objects.filter(username__icontains=query,is_academy=True).values('username')
            trials = Trial.objects.filter(name__icontains=query).values('name')

            suggestions = []
            suggestions.extend([{'name': player['username'], 'type': 'Player'} for player in players])
            suggestions.extend([{'name': academy['username'], 'type': 'Academy'} for academy in academies])
            # suggestions.extend([{'name': post['title'], 'type': 'Post'} for post in posts])
            suggestions.extend([{'name': trial['name'], 'type': 'Trial'} for trial in trials])

            return JsonResponse(suggestions, safe=False)
        return JsonResponse({'message': 'No query provided.'}, status=400)
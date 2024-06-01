from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager

from common.base_models import DataBaseModels


class CustomUserManager(BaseUserManager):
    def create_user(self,email,username=None, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email,username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        print('create user manager')
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        print('create superuser manager')
        return self.create_user(email, password, **extra_fields)

 
class Users(AbstractUser):
    username = models.CharField(max_length=255, blank=True,null=True )
    email = models.EmailField(unique=True, max_length=255)
    phone = models.CharField(max_length=15,null=True,blank=True)
    otp = models.CharField(max_length=10, null=True, blank=True)
    dob = models.DateField(null=True,blank=True)  #established date for academy
    is_academy = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]
    objects = CustomUserManager()

    def __str__(self) -> str:
        return self.username + 'user instance'


class Sport(DataBaseModels):
    sport_name = models.CharField(max_length=255)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.user.username + self.sport_name + 'sport instance'


class UserProfile(DataBaseModels):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, null=True)
    bio = models.TextField(null=True, blank=True)
    about = models.TextField(null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    district = models.CharField(max_length=255, null=True, blank=True)
    profile_photo = models.ImageField(upload_to='medias/',null=True, blank=True)
    cover_photo = models.ImageField(upload_to='medias/',null=True, blank=True)


    def __str__(self):
        return self.user.username + 'profile instance' + self.bio
    



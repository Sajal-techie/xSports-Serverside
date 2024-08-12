from datetime import timedelta

from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from common.custom_permission_classes import IsAdmin, IsPlayer
from post.models import Post
from selection_trial.models import PlayersInTrial, Trial
from users.models import Academy, Sport, UserProfile, Users
from users.serializers.user_serializer import (Academyserializer,
                                               SportSerializer,
                                               UserProfileSerializer)

from .task import send_alert


class AcademyManage(APIView):
    permission_classes = [IsAuthenticated, IsAdmin | IsPlayer]

    def get(self, request):
        users = Users.objects.filter(is_academy=True).order_by("-id")
        user_data = []
        for user in users:
            if UserProfile.objects.filter(user=user).exists():
                user_profile = UserProfile.objects.get(user=user)
            if Sport.objects.filter(user=user).exists():
                sports = Sport.objects.filter(user=user)
                sport_data = []
                for sport in sports:
                    sport_data.append(SportSerializer(sport).data)
            if Academy.objects.filter(user=user).exists():
                academy_data = Academy.objects.get(user=user)
            user_data.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "dob": user.dob,
                    "profile": UserProfileSerializer(user_profile).data,
                    "sport": sport_data,
                    "academy_data": Academyserializer(academy_data).data,
                }
            )
        if not user_data:
            return Response(
                {"academy": user_data, "status": status.HTTP_204_NO_CONTENT}
            )
        return Response({"academy": user_data, "status": status.HTTP_200_OK})


class ToggleIsCertified(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, id):
        try:
            value = request.data.get("value", None)
            user = Users.objects.get(id=id)
            academy = Academy.objects.get(user=user)
            if value:
                if value == "approve":
                    subject = "Your account has Approved by Admin"
                    message = f" Now you can login {settings.SITE_URL} to xSports"
                    academy.is_certified = True
                else:
                    subject = "Your account has been Denied by admin"
                    message = f"Your xSports account with email {user.email} has been denied by admin"
                    academy.is_certified = False
                email_from = settings.EMAIL_HOST_USER
                send_alert.delay(subject, message, email_from, [user.email])
            academy.save()
            return Response(
                {
                    "status": status.HTTP_200_OK,
                    "message": "Certification updated successfully",
                }
            )
        except Exception as e:
            print(e, "error in certification update")
            return Response(
                {"status": status.HTTP_400_BAD_REQUEST, "message": "some error"}
            )


class PlayerManage(APIView):

    def get(self, request):
        players = Users.objects.filter(
            Q(is_academy=False) & Q(is_staff=False) & Q(is_superuser=False)
        ).order_by("-id")
        player_data = []
        for user in players:
            if UserProfile.objects.filter(user=user).exists():
                user_profile = UserProfile.objects.get(user=user)
            if Sport.objects.filter(user=user).exists():
                sports = Sport.objects.filter(user=user)
                sport_data = []
                for sport in sports:
                    sport_data.append(SportSerializer(sport).data)
            player_data.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "dob": user.dob,
                    "is_active": user.is_active,
                    "profile": UserProfileSerializer(user_profile).data,
                    "sport": sport_data,
                }
            )
        if not player_data:
            return Response(
                {"player": player_data, "status": status.HTTP_204_NO_CONTENT}
            )

        return Response({"player": player_data, "status": status.HTTP_200_OK})


class ToggleActive(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, id):
        try:
            value = request.data.get("value", None)
            user = Users.objects.get(id=id)
            if value:
                if value == "active":
                    user.is_active = True
                    user.save()
                else:
                    user.is_active = False
                    user.save()

            return Response(
                {"status": status.HTTP_200_OK, "message": "Updated successfully"}
            )
        except Exception as e:
            print(e,'user acitvaiton failed')
            return Response(
                {"status": status.HTTP_400_BAD_REQUEST, "message": "Updation failed"}
            )


class DashboardViewSet(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, *args, **kwargs):

        today = timezone.now()
        start_of_the_week = today - timedelta(days=today.weekday())

        #  to fetch weekly perecentage increase of new users
        total_players = Users.objects.filter(is_academy=False, is_staff=False).count()
        players_joined_this_week = Users.objects.filter(
            is_academy=False, is_staff=False, created_at__gte=start_of_the_week
        ).count()

        if total_players > 0:
            player_percentage_joined_this_week = (
                players_joined_this_week / total_players
            ) * 100
        else:
            player_percentage_joined_this_week = 0

        #  to fetch weekly percentage increase of academies
        total_academies = Users.objects.filter(is_academy=True, is_staff=False).count()
        academies_joined_this_week = Users.objects.filter(
            is_academy=True, is_staff=False, created_at__gte=start_of_the_week
        ).count()
        if total_academies > 0:
            academy_percentage_joined_this_week = (
                players_joined_this_week / total_players
            ) * 100
        else:
            academy_percentage_joined_this_week = 0

        # to fetch weekly percentage of trials
        total_trials = Trial.objects.filter(is_active=True).count()
        trials_created_this_week = Trial.objects.filter(
            is_active=True, created_at__gte=start_of_the_week
        ).count()
        if total_trials > 0:
            trial_percentage_this_week = (trials_created_this_week / total_trials) * 100
        else:
            trial_percentage_this_week = 0

        weekly_data = [
            {
                "total": total_players,
                "this_week": players_joined_this_week,
                "percentage_this_week": player_percentage_joined_this_week,
                "text": "Players Joined this Week",
            },
            {
                "total": total_academies,
                "this_week": academies_joined_this_week,
                "percentage_this_week": academy_percentage_joined_this_week,
                "text": "Academies Joined this Week",
            },
            {
                "total": total_trials,
                "this_week": trials_created_this_week,
                "percentage_this_week": trial_percentage_this_week,
                "text": "Trials created this Week ",
            },
        ]

        total_posts = Post.objects.count()
        # fetching total count for visualising in graph
        stats = {
            "totalAcademies": total_academies,
            "totalPlayers": total_players,
            "totalTrials": total_trials,
            "totalPosts": total_posts,
        }

        recent_players = (
            Users.objects.filter(is_academy=False, is_staff=False)
            .values(
                "username",
                "created_at",
                "userprofile__profile_photo",
                "userprofile__state",
                "userprofile__district",
            )
            .order_by("-created_at")[:5]
        )

        recent_academies = (
            Users.objects.filter(is_academy=True, is_staff=False)
            .values(
                "username",
                "created_at",
                "userprofile__profile_photo",
                "userprofile__state",
                "userprofile__district",
            )
            .order_by("-created_at")[:5]
        )

        recent_trials = (
            Trial.objects.filter(
                is_active=True,
            )
            .values(
                "name",
                "created_at",
                "trial_date",
                "registration_fee",
                "sport",
                "is_registration_fee",
            )
            .order_by("-created_at")[:7]
        )

        return Response(
            data={
                "players": recent_players,
                "academies": recent_academies,
                "trials": recent_trials,
                "weekly_data": weekly_data,
                "stats": stats,
            },
            status=status.HTTP_200_OK,
        )


class AccountsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):

        payments = PlayersInTrial.objects.filter(
            trial__is_registration_fee=True, trial__is_active=True
        )
        payment_summary = []

        academy_payments = {}

        for payment in payments:
            academy = payment.trial.academy
            fee = payment.trial.registration_fee

            if academy.id in academy_payments:
                academy_payments[academy.id]["total_amount"] += fee
            else:
                academy_payments[academy.id] = {
                    "academy_id": academy.id,
                    "academy_name": academy.username, 
                    "total_amount": fee,
                }

        payment_summary = list(academy_payments.values())

        return Response(payment_summary)

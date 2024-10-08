from datetime import date
import stripe
import stripe.error
from common.custom_pagination_class import StandardResultsSetPagination
from common.custom_permission_classes import (IsAcademy, IsAdmin, IsPlayer,
                                              IsUser)
from django.conf import settings
from django.db import transaction
from django.db.models import Count, Q
from rest_framework import generics, response, status, viewsets

from .models import PlayersInTrial, Trial
from .serializers import (PlayersInTrialSerializer, TrialHistorySerializer,
                          TrialSerializer)
from .tasks import send_status_mail, send_trial_cancellation_mail

# Set Stripe API key and webhook secret from settings
stripe.api_key = settings.STRIPE_SECRET_KEY
webhook_secret = settings.STRIPE_WEBHOOK_SECRET


class TrialViewSet(viewsets.ModelViewSet):
    """
    API view to manage trials.

    Attributes:
        queryset: The queryset for the Trial model.
        serializer_class: The serializer class for the Trial model.
        lookup_field: The field used to look up the Trial instance.
    """
    queryset = Trial.objects.all()
    serializer_class = TrialSerializer
    lookup_field = "id"

    def get_permissions(self):
        """
        Determine the permissions based on the action.

        Returns:
            list: A list of permission classes to be used for the request.
        """
        if self.action in ["list", "retrieve", "player_detials_in_trial"]:
            permission_classes = [IsUser | IsAdmin]
        else:
            permission_classes = [IsAcademy]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Get the queryset for the view based on filtering parameters.

        Returns:
            queryset: The filtered queryset for the Trial model.
        """
        user = self.request.user
        queryset = (
            Trial.objects.all()
            .annotate(player_count=Count("trial"))
            .order_by("trial_date")
        )
        search_term = self.request.query_params.get("search", None)
        sport = self.request.query_params.get("sport", None)
        state = self.request.query_params.get("state", None)
        payment = self.request.query_params.get("payment", None)
        academy_id = self.request.query_params.get("id", None)

        if search_term:
            queryset = queryset.filter(
                Q(name__icontains=search_term)
                | Q(description__icontains=search_term)
                | Q(academy__username__icontains=search_term)
                | Q(sport__icontains=search_term)
            )

        if sport:
            queryset = queryset.filter(sport=sport)

        if state:
            queryset = queryset.filter(state=state)

        if payment:
            payment = False if payment == "false" else True
            queryset = queryset.filter(is_registration_fee=payment)

        if user.is_staff:
            queryset = queryset.order_by("id")
            self.pagination_class = StandardResultsSetPagination
            return queryset

        if academy_id:
            queryset = queryset.filter(academy=academy_id, is_active=True)
            return queryset

        if user.is_academy:
            # Filter trials created by the current academy
            queryset = queryset.filter(academy=user, is_active=True)
            return queryset

        # Filter trials for players with trial dates in the future
        today = date.today()
        self.pagination_class = StandardResultsSetPagination
        queryset = queryset.filter(
            trial_date__gte=today, is_active=True
        ).select_related("academy")
        return queryset

    def retrieve(self,request, id):
        """
        Retrieve a specific trial by its ID.

        Args:
            request: The HTTP request object.
            id: The ID of the trial to retrieve.

        Returns:
            response: The trial details or an error response.
        """
        try:
            trial = (
                Trial.objects.filter(id=id)
                .annotate(player_count=Count("trial"))
                .first()
            )
        except Exception as e:
            return response.Response(data="Not found", status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(trial)
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, id):
        """
        Mark a trial as inactive and notify registered players if the trial is canceled.

        Args:
            request: The HTTP request object.
            id: The ID of the trial to delete.

        Returns:
            response: A response indicating the success or failure of the operation.
        """

        reason = request.query_params.get("reason", None)
        trial = Trial.objects.get(id=id)
        players_in_trial = PlayersInTrial.objects.filter(trial=trial)

        recipient_list = [player.email for player in players_in_trial]
        if recipient_list:
            send_trial_cancellation_mail.delay(
                recipient_list, trial.name, trial.academy.username, reason
            )
        trial.is_active = False
        trial.save()
        return response.Response(status=status.HTTP_200_OK)

    def player_detials_in_trial(self, request, id=None):
        """
        Fetch the details of the user registered for a specific trial.

        Args:
            request: The HTTP request object.
            id: The ID of the trial.

        Returns:
            response: The player details or a no-content response if not registered.
        """
        user = request.user
        if not PlayersInTrial.objects.filter(player=user, trial=id).exists():
            return response.Response(status=status.HTTP_204_NO_CONTENT)

        player_details = PlayersInTrial.objects.get(player=user, trial=id)
        if (
            player_details.trial.is_registration_fee
            and player_details.payment_status == "pending"
        ):
            # Remove player details if payment is pending
            player_details.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        serializer = PlayersInTrialSerializer(player_details)
        return response.Response(serializer.data, status=status.HTTP_200_OK)


class PlayersInTrialViewSet(viewsets.ModelViewSet):
    """
    API view to manage players in trials.

    Attributes:
        queryset: The queryset for the PlayersInTrial model.
        serializer_class: The serializer class for the PlayersInTrial model.
        lookup_field: The field used to look up the PlayersInTrial instance.
        permission_classes: The permissions required for this view.
    """

    queryset = PlayersInTrial.objects.all()
    serializer_class = PlayersInTrialSerializer
    lookup_field = "id"
    permission_classes = [IsUser]

    @transaction.atomic
    def create(self, request):
        """
        Register a player for a trial and handle payment if required.

        Args:
            request: The HTTP request object.

        Returns:
            Response: The registration details or an error response.
        """

        trial_id = request.data.get("trial")
        try:
            trial = Trial.objects.get(id=trial_id)
        except Exception as e:
            print(e, 'trial not found')
            return response.Response(data="Trial not found", status=status.HTTP_404)
        playercount = PlayersInTrial.objects.filter(trial=trial).count()

        # Check if the participant limit is exceeded
        if trial.is_participant_limit and playercount >= trial.total_participant_limit:
            return response.Response(
                data="Participant limit exceeded", status=status.HTTP_406_NOT_ACCEPTABLE
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Complete registration if no payment is required
        if not trial.is_registration_fee:
            self.perform_create(serializer)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)

        player_registration = serializer.save(payment_status="pending")
        try:
            # Create a Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        "price_data": {
                            "currency": "inr",
                            "product_data": {
                                "name": trial.name,
                            },
                            "unit_amount": int(trial.registration_fee * 100),
                        },
                        "quantity": 1,
                    },
                ],
                mode="payment",
                success_url=f"{settings.SITE_URL}/payment_success?registrationId={player_registration.id}&trialId={trial.id}",
                cancel_url=f"{settings.SITE_URL}/payment_failed?registrationId={player_registration.id}&trialId={trial.id}", 
                client_reference_id=player_registration.id,
            )

           # Return the Stripe session ID to the frontend
            return response.Response(
                {
                    "sessionId": checkout_session.id,
                    "registration_id": player_registration.id,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            print(
                e, " exepriton in strip deleting user resgistraion", player_registration
            )
            # Delete registration if payment fails
            player_registration.delete()
            return response.Response(
                {"message": "error in stripe payment"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def list_players_in_trial(self, request, trial_id=None):
        """
        List all players registered for a specific trial.

        Args:
            request: The HTTP request object.
            trial_id: The ID of the trial.

        Returns:
            Response: A list of players registered for the trial.
        """
        players = (
            self.queryset.filter(trial=trial_id)
            .prefetch_related("playersintrial")
            .order_by("id")
        )
        serialzer = self.get_serializer(players, many=True)
        return response.Response(serialzer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, id):
        """
        Update the status of a player's registration and send a notification email.

        Args:
            request: The HTTP request object.
            id: The ID of the player's registration.

        Returns:
            Response: A response indicating the success or failure of the update.
        """
        player = PlayersInTrial.objects.get(id=id)
        if request.data["status"] == "selected":
            message = f"""We are excited to inform you that  you are selected in the 
                        {player.trial.name}'s conducted by {player.trial.academy.username} 
                        academy ,
                        further information will be provided please stay tuned"""
        else:
            message = f"""We are sorry to inform that  you are not seleted in the 
                        {player.trial.name}'s conducted by {player.trial.academy.username} 
                        academy ,
                        Thank you for you participation . """
 
        send_status_mail.delay(
            email=player.email, trial_name=player.trial.name, message=message
        )
        player.status = request.data.get("status", "registered")
        player.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    # to update payment satus and confirm registration
    def update(self, request, id):
        registration = PlayersInTrial.objects.get(id=id)
        registration.payment_status = "confirmed"
        registration.save()
        return response.Response(
            data="Payment confirmed and Registration Completed",
            status=status.HTTP_200_OK,
        )

    # delete player regsitraion if payement is not compelted
    def destroy(self, request, id, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class TrialHistory(generics.ListAPIView):
    """
    API view to get the history of trials for a player.

    Attributes:
        serializer_class: The serializer class for the TrialHistory model.
        pagination_class: The pagination class for the results.
    """
    serializer_class = TrialHistorySerializer
    permission_classes = [IsPlayer]
    queryset = PlayersInTrial.objects.all()

    def get_queryset(self):
        user = self.request.user
        return (
            PlayersInTrial.objects.filter(player=user)
            .select_related("trial")
            .order_by("-id")
        )

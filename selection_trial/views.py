from rest_framework import viewsets,views,response,status
from rest_framework.decorators import action
from datetime import date
from django.db.models import Count
from django.conf import settings
from django.db import transaction
import stripe
import stripe.error
from .models import Trial,PlayersInTrial
from .serializers import TrialSerializer,PlayersInTrialSerializer
from common.custom_permission_classes import IsAcademy,IsPlayer,IsUser,IsAdmin
from .tasks import send_status_mail,send_trial_cancellation_mail

stripe.api_key = settings.STRIPE_SECRET_KEY
webhook_secret = settings.STRIPE_WEBHOOK_SECRET

class TrialViewSet(viewsets.ModelViewSet):
    queryset = Trial.objects.all() 
    serializer_class = TrialSerializer
    lookup_field = 'id'
    permission_classes = [IsUser]

    def get_queryset(self):
        user = self.request.user
        if user.is_academy:
            # if requested by academy then only show only the trial created by them 
            return Trial.objects.filter(academy = user,is_active=True).annotate(player_count=Count('trial')).order_by('-trial_date')
        today = date.today()
        
        # if requested by players then show all trials with trialdate less than today's date
        return Trial.objects.filter(trial_date__gte=today,is_active=True).annotate(player_count=Count('trial')).select_related('academy').order_by('trial_date')

    def retrieve(self, request, *args, **kwargs):
        print(request.data, args,kwargs)
        return super().retrieve(request, *args, **kwargs)
    
    # make trial is_active to false if trial cancelled by academy 
    def destroy(self, request,id, *args, **kwargs):
        print(self,request,args, kwargs,id) 
        trial = Trial.objects.get(id=id)
        players_in_trial = PlayersInTrial.objects.filter(trial=trial)

        recipient_list = [player.email for player in players_in_trial]
        print(recipient_list,'emails-------')
        if recipient_list:
            send_trial_cancellation_mail.delay(recipient_list,trial.name,trial.academy.username)
        trial.is_active = False
        trial.save()
        return response.Response(status=status.HTTP_200_OK)
    
    # to fetch details of the user (if registered)  white viewing trial details
    def player_detials_in_trial(self,request,id=None,*args, **kwargs):
        user = request.user
        print(user,id,args, kwargs,' player details trial')
        if not PlayersInTrial.objects.filter(player=user,trial=id).exists():
            return response.Response(status=status.HTTP_204_NO_CONTENT)

        player_details = PlayersInTrial.objects.get(player=user,trial=id)
        if player_details.payment_status == 'pending':
            # if the payment is not completed then remove the data 
            player_details.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        serializer = PlayersInTrialSerializer(player_details)
        print(serializer.data, 'in player detials trial')
        return response.Response(serializer.data,status=status.HTTP_200_OK)


class PlayersInTrialViewSet(viewsets.ModelViewSet):
    queryset = PlayersInTrial.objects.all()
    serializer_class = PlayersInTrialSerializer
    lookup_field = 'id'
    permission_classes = [IsUser]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        trial_id = request.data.get('trial')
        try:
            trial = Trial.objects.get(id=trial_id)
        except Exception as e:
            print(e)
            return response.Response(data='Trial not found',status=status.HTTP_404)  
        print(trial_id,trial,' in create')
        playercount =  PlayersInTrial.objects.filter(trial=trial).count() 
        print(playercount,'-------playercount------')

        # if participant limit exceed current regsitered players return error
        if trial.is_participant_limit and playercount >= trial.total_participant_limit:
            return response.Response(data='Participant limit exceeded',status=status.HTTP_406_NOT_ACCEPTABLE)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True) 

        # if there is no payement make registration complete
        if not trial.is_registration_fee:
            print('no payment registed and returnong')
            self.perform_create(serializer)
            return response.Response(serializer.data, status=status.HTTP_201_CREATED) 

        player_registration = serializer.save(payment_status='pending')
        print(player_registration,player_registration.status,' payment needed')
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                        {
                            'price_data' :{
                            'currency' : 'inr',  
                                'product_data': {
                                'name': trial.name,
                                },
                            'unit_amount': int(trial.registration_fee * 100)
                            },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=f'{settings.SITE_URL}/payment_success?registrationId={player_registration.id}&trialId={trial.id}', # payment successs page is set in frontend
                cancel_url=f'{settings.SITE_URL}/payment_failed?registrationId={player_registration.id}&trialId={trial.id}', # payement failed page is set in frontend
                client_reference_id=player_registration.id
            )
            print('afte stripe intent')

            # if payment is needed the sesssion id is send to frontend for stripe checkout page
            return response.Response({
                'sessionId':checkout_session.id,
                'registration_id' : player_registration.id
            },status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e,' exepriton in strip deleting user resgistraion',player_registration)
            # if payement is cancelled delete the current regsitration
            player_registration.delete()
            return response.Response({'message':"error in stripe payment"},status=status.HTTP_400_BAD_REQUEST)

    # to list players joined in a trial 
    def list_players_in_trial(self,request,trial_id=None):
        print(trial_id,request,request.data)
        players = self.queryset.filter(trial=trial_id).prefetch_related('playersintrial').order_by('id')
        serialzer = self.get_serializer(players,many=True)
        print(serialzer.data)
        return response.Response(serialzer.data,status=status.HTTP_200_OK)

    # to udpate player status(by academy) and send notification mail
    def partial_update(self, request,id, *args, **kwargs):
        print(request,request.data,args, kwargs,id)
        player = PlayersInTrial.objects.get(id=id)
        print(player)
        if request.data['status'] == 'selected':    
            message = f"""We are excited to inform you that  you are selected in the 
                        {player.trial.name}'s conducted by {player.trial.academy.username} academy ,
                        further information will be provided please stay tuned"""
        else:
            message = f"""We are sorry to inform that  you are not seleted in the 
                        {player.trial.name}'s conducted by {player.trial.academy.username} academy , 
                        Thank you for you participation . """
        send_status_mail.delay(email=player.email,trial_name=player.trial.name,message=message)
        return super().partial_update(request, *args, **kwargs)
    
    # to update payment satus and confirm registration
    def update(self, request,id, *args, **kwargs):
        print(id,self.get_object(),args,kwargs,'in updation cofirmed')
        registration = PlayersInTrial.objects.get(id=id)
        registration.payment_status = 'confirmed'
        registration.save()
        print('status changed now returning,',registration.status,registration.payment_status)
        return response.Response(data="Payment confirmed and Registration Completed",status=status.HTTP_200_OK)
    
    # to delete player regsitraion if payement is not compelted
    def destroy(self, request,id, *args, **kwargs):
        print(request.data,id,args,kwargs,'in delete registration')
        # PlayersInTrialDetails.objects.filter(player_trial=id).delete()
        return super().destroy(request, *args, **kwargs)
    

# to check if player joined in a trial and return its id
# class PlayerExistInTrialView(views.APIView):
#     def get(self,request,id,*args, **kwargs):
#         user = request.user
#         total_count = PlayersInTrial.objects.filter(trial=id).count() 
#         if PlayersInTrial.objects.filter(player=user,trial=id).exists():
#             print('hai',id,*args, **kwargs)
#             player_trial = PlayersInTrial.objects.get(player=user,trial=id)
#             print(player_trial.status,player_trial.unique_id,total_count)
#             return response.Response(data={
#                 'status':player_trial.status,
#                 'unique_id':player_trial.unique_id,
#                 'count':total_count
#             },status=status.HTTP_200_OK)
#         else:
#             print(total_count)
#             return response.Response(data={'count':total_count},status=status.HTTP_206_PARTIAL_CONTENT) 
        
# to create stripe intent and return id to front end
# class StripeCheckoutView(views.APIView):
#     def post(self,request,id,*args, **kwargs):
#         try:
#             data =  request.data
#             print(args,kwargs,id,data)
#             trial = Trial.objects.get(id=id)
#             pending_reg_id = data['pending_reg_id'] # id of player to change payment status
#             # price = data['price']
#             # product_name = data['product_name']
#             print('in stripe checkout view ',request.data,trial)
#             checkout_session = stripe.checkout.Session.create(
#                 line_items=[
#                         {
#                             'price_data' :{
#                             'currency' : 'inr',  
#                                 'product_data': {
#                                 'name': trial.name,
#                                 },
#                             'unit_amount': int(trial.registration_fee * 100)
#                             },
#                         'quantity': 1,
#                     },
#                 ],
#                 mode='payment',
#                 success_url=f'{settings.SITE_URL}/payment_success?registrationId={pending_reg_id}&trialId={trial.id}',
#                 cancel_url=f'{settings.SITE_URL}/payment_failed?registrationId={pending_reg_id}&trialId={trial.id}',
#                 client_reference_id=pending_reg_id
#             )
#             print('going to redirect')
#             # return redirect(checkout_session.url)
#             return response.Response({'sessionId':checkout_session.id})
        
#         except Exception as e:
#             print(e, ' eeor in stripe checkout')
#             return response.Response({
#                 'error':'Some eror in response',
#                 'status':status.HTTP_500_INTERNAL_SERVER_ERROR
#                 })
 

# class WebHook(views.APIView):
#     def post(self,request):
#         print('in webhook view')
#         event = None
#         payload = request.body
#         sig_header = request.META['HTTP_STRIPE_SIGNATURE']
#         try:
#             event = stripe.Webhook.construct_event(
#                 payload,sig_header,webhook_secret
#             )
#             print(event, ' event')
#         except ValueError as err:
#             print(err, 'value error')
#             raise err
#         except stripe.error.SignatureVerificationError as err:
#             print(err, 'signature verification error')
#             raise err
#         except Exception as e:
#             print(e, 'exception ouw')

#         if event['type'] == 'checkout.session.completed':
#             session = event['data']['object']
#             registration_id = session['client_reference_id']
#             players_in_trial_viewset = PlayersInTrialViewSet()
#             return players_in_trial_viewset.confirm_payment(registration_id)
#         elif event['type'] == 'checkout.session.expired':
#             session = event['data']['object']
#             registration_id = session['client_reference_id']
#             players_in_trial_viewset = PlayersInTrialViewSet()
#             return players_in_trial_viewset.cancel_payment(registration_id)
#         else:
#             return response.Response({"message": f"Unhandled event type {event['type']}"}, status=status.HTTP_200_OK)
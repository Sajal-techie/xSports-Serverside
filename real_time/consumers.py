import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.conf import settings
from .models import Chat,Users, Notification
from .serializers import ChatSerializer

class PersonalChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("inside the socker consumer")
        self.room_name = self.scope['url_route']['kwargs']['thread_name']
        print(self.room_name,'roomname')
        self.room_group_name = f'{self.room_name}'
        print(self.room_name,self.room_group_name,'room name group name')

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
    
        await self.accept()
    
    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        print(data, text_data,'data')
        message = data['message']
        sender_id = data['sender']
        receiver_id = data['receiver']

        print(message, sender_id, receiver_id, data,text_data,' in receive')

        sender = await self.get_user(sender_id)
        receiver = await self.get_user(receiver_id)

        if sender and receiver:
            chat = await self.save_message(sender,receiver, message)

            serialized_data = await self.serialize_chat(chat)
            print(serialized_data,chat,'chat message, sereializer')

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message_data': serialized_data
                }
            )
            link = '/chat/'+self.room_name
            text =  f"New message from {sender.username}"
            notification_type = 'new_message'

            await self.channel_layer.group_send(
                f"notification_{receiver_id}",
                {
                    'type': 'send_notification',
                    'data':{
                        'type': notification_type,
                        'sender': sender.username,
                        'message': message,
                        'link': link,
                        'text': text
                    }
                }
            )
            await create_notification(sender=sender, receiver=receiver, link=link, text=text, notification_type=notification_type )
        else:
            print(f"Error: Sender {sender_id} or Receiver {receiver_id} not found")
    
    async def chat_message(self, event):
        print(event, 'event',timezone.now())
        message_data = event['message_data']
        await self.send(text_data=json.dumps(message_data))


    @database_sync_to_async
    def get_user(self,user_id):
        try:
            return Users.objects.get(id=user_id)
        except Exception as e:
            return None

    @database_sync_to_async
    def save_message(self, sender, receiver, message):
        print(sender, receiver, 'user')
        chat = Chat.objects.create(sender=sender, receiver=receiver,message=message,thread_name=self.room_name)
        return chat
    
    @database_sync_to_async
    def serialize_chat(self,chat):
        return ChatSerializer(chat).data


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.notification_group_name = f'notification_{self.user_id}'
        print(self.user_id, 'current user', self.notification_group_name)
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.notification_group_name,
            self.channel_name
        )

    # async def receive(self, text_data=None, bytes_data=None):
    #     data = json.loads(text_data)
    #     print(data)
    #     message = data['message']

    #     await self.channel_layer.group_send(
    #         f"notificaton_{self.user_id}",
    #         {
    #             'type': 'send_notification',
    #             'message': message
    #         }
    #     )

    async def send_notification(self, event):
        print(event, 'event')
        await self.send(text_data=json.dumps(event['data']))


@database_sync_to_async
def create_notification(sender, receiver, notification_type, text, link = None):
    return Notification.objects.create(
        sender=sender,
        receiver=receiver,
        notification_type=notification_type,
        text=text,
        link=link,
        seen=False
    )
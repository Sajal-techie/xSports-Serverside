import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Chat,Users
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
        # saved_messsage = await self.save_message(sender, receiver, message)
        # serializer = ChatSerializer(saved_messsage).data # serialize the data (to get related fields also)
        # serializer_data = serializer.data
            serialized_data = await self.serialize_chat(chat)
            print(serialized_data,chat,'chat message, sereializer')

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message_data': serialized_data
                }
            )
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
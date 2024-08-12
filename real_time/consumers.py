import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Chat, Notification, Users
from .serializers import ChatSerializer


class PersonalChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling personal chat messages between users.

    Methods:
        connect(): Called when a WebSocket connection is established.
        disconnect(code): Called when the WebSocket connection is closed.
        receive(text_data=None, bytes_data=None): Called when a message is received from the WebSocket.
        chat_message(event): Sends chat message data to the WebSocket.
    """
    async def connect(self):
        """
        Called when the WebSocket connection is established.
        Adds the WebSocket to the appropriate group for the chat thread.
        """
        self.room_name = self.scope["url_route"]["kwargs"]["thread_name"]
        self.room_group_name = f"{self.room_name}"

        # Join the chat group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        """
        Called when the WebSocket connection is closed.
        Removes the WebSocket from the chat group.
        """
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        """
        Called when a message is received from the WebSocket.
        Handles saving the chat message, broadcasting it to the chat group,
        and sending notifications to the receiver.

        Args:
            text_data (str): The message data received from the WebSocket.
        """
        data = json.loads(text_data)
        message = data["message"]
        sender_id = data["sender"]
        receiver_id = data["receiver"]

        sender = await self.get_user(sender_id)
        receiver = await self.get_user(receiver_id)

        if sender and receiver:
            chat = await self.save_message(sender, receiver, message)

            serialized_data = await self.serialize_chat(chat)

            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "chat_message", "message_data": serialized_data},
            )
            link = f"/chat/{self.room_name}"
            text = f"New message from {sender.username}"
            notification_type = "new_message"

            # Send notification to the receiver
            await self.channel_layer.group_send(
                f"notification_{receiver_id}",
                {
                    "type": "send_notification",
                    "data": {
                        "type": notification_type,
                        "sender": sender.username,
                        "message": message,
                        "link": link,
                        "text": text,
                    },
                },
            )
            await create_notification(
                sender=sender,
                receiver=receiver,
                link=link,
                text=text,
                notification_type=notification_type,
            )

    async def chat_message(self, event):
        """
        Sends chat message data to the WebSocket.

        Args:
            event (dict): The event data containing the message data.
        """
        message_data = event["message_data"]
        await self.send(text_data=json.dumps(message_data))

    @database_sync_to_async
    def get_user(self, user_id):
        """
        Retrieves a user from the database by ID.

        Args:
            user_id (int): The ID of the user to retrieve.

        Returns:
            Users: The user object if found, otherwise None.
        """
        try:
            return Users.objects.get(id=user_id)
        except Exception as e:
            print(e, 'User does not exist')
            return None

    @database_sync_to_async
    def save_message(self, sender, receiver, message):
        """
        Saves a chat message to the database.

        Args:
            sender (Users): The user sending the message.
            receiver (Users): The user receiving the message.
            message (str): The content of the message.

        Returns:
            Chat: The saved chat object.
        """
        chat = Chat.objects.create(
            sender=sender,
            receiver=receiver,
            message=message,
            thread_name=self.room_name,
        )
        return chat

    @database_sync_to_async
    def serialize_chat(self, chat):
        """
        Serializes a chat object to JSON format.

        Args:
            chat (Chat): The chat object to serialize.

        Returns:
            dict: The serialized chat data.
        """
        return ChatSerializer(chat).data


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling notifications for a specific user.

    Methods:
        connect(): Called when a WebSocket connection is established.
        disconnect(code): Called when the WebSocket connection is closed.
        send_notification(event): Sends notification data to the WebSocket.
    """
     
    async def connect(self):
        """
        Called when the WebSocket connection is established.
        Adds the WebSocket to the appropriate group for notifications of the user.
        """
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.notification_group_name = f"notification_{self.user_id}"
        await self.channel_layer.group_add(
            self.notification_group_name, self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        """
        Called when the WebSocket connection is closed.
        Removes the WebSocket from the notification group.
        """
        await self.channel_layer.group_discard(
            self.notification_group_name, self.channel_name
        )

    async def send_notification(self, event):
        """
        Sends notification data to the WebSocket.

        Args:
            event (dict): The event data containing the notification data.
        """
        await self.send(text_data=json.dumps(event["data"]))


@database_sync_to_async
def create_notification(sender, receiver, notification_type, text, link=None):
    """
    Creates a notification object in the database.

    Args:
        sender (Users): The user who triggered the notification.
        receiver (Users): The user who will receive the notification.
        notification_type (str): The type of the notification.
        text (str): The content of the notification.
        link (str, optional): A URL associated with the notification.

    Returns:
        Notification: The created notification object.
    """
    
    return Notification.objects.create(
        sender=sender,
        receiver=receiver,
        notification_type=notification_type,
        text=text,
        link=link,
        seen=False,
    )

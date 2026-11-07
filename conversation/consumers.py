import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Conversation, ConversationMessage
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()

class ConversationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        
        try:
            conversation = await sync_to_async(Conversation.objects.get)(pk=self.conversation_id)
            user = self.scope["user"]
            
            is_member = await sync_to_async(conversation.members.filter(id=user.id).exists)()
            if not is_member:
                await self.close(code=4001)
                return
                
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            
        except ObjectDoesNotExist:
            await self.close(code=4002)
        except Exception as e:
            print(f"Connection error: {e}")
            await self.close(code=4000)

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_content = data.get('message', '').strip()
            sender_username = data.get('sender')
            
            if not message_content or not sender_username:
                raise ValueError("Missing required fields")
            conversation = await sync_to_async(Conversation.objects.get)(pk=self.conversation_id)
            sender = await sync_to_async(User.objects.get)(username=sender_username)
            
            await sync_to_async(setattr)(conversation, 'modified_at', timezone.now())
            await sync_to_async(conversation.save)()
            
            message = await sync_to_async(ConversationMessage.objects.create)(
                conversation=conversation,
                content=message_content,
                created_by=sender
            )
            members = await sync_to_async(list)(conversation.members.all())
            for member in members:
                if member.id != sender.id:
                    cache_key = f"unread_{member.id}_{conversation.id}"
                    try:
                        existing_count = await sync_to_async(cache.get)(cache_key)
                        if existing_count is None:
                            current_count = 1
                            await sync_to_async(cache.set)(cache_key, current_count, timeout=300)
                        else:
                            current_count = await sync_to_async(cache.incr)(cache_key)
                        
                        await self.channel_layer.group_send(
                            f"user_{member.id}",
                            {
                                "type": "unread_update",
                                "conversation_id": conversation.id,
                                "count": current_count
                            }
                        )
                    except Exception as e:
                        print(f"Unread count error: {e}")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message.content,
                    'sender': sender.username,
                    'timestamp': message.created_at.isoformat(),
                    'message_id': str(message.id)
                }
            )

        except json.JSONDecodeError:
            await self.send_error('Invalid JSON format')
        except Exception as e:
            await self.send_error(str(e))

    async def send_error(self, message):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id']
        }))

    async def unread_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "unread_update",
            "conversation_id": event["conversation_id"],
            "count": event["count"]
        }))

class UserNotificationsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.user_group_name = f'user_{self.user_id}'
        
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'mark_read':
            conversation_id = data['conversation_id']
            cache_key = f'unread_{self.user_id}_{conversation_id}'
            await sync_to_async(cache.set)(cache_key, 0)

    async def unread_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "unread_update",
            "conversation_id": event["conversation_id"],
            "count": event["count"]
        }))




        
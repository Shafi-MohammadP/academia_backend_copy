import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime


class AdminNotifications(AsyncWebsocketConsumer):
    async def connect(self):
        from notifications.models import Notifications
        try:
            self.group_name = 'admin_group'
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            print('connected ')
            await self.accept()
        except Exception as e:
            print("Error in connect in admin notification", e)

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        except Exception as e:
            print("Error in disconnect admin notif:", e)

    async def receive(self, text_data):
        try:
            message = json.loads(text_data)
            print("admin_Received message:", message)
        except Exception as e:
            print("Error in receive admin noti:", e)

    async def create_notification(self, event):
        try:
            message = event['message']

            await self.send(json.dumps({

                'message': message,


            }))
        except Exception as e:
            print("Error in create admin notifications", e)


class TutorNotification(AsyncWebsocketConsumer):
    async def connect(self):
        from notifications.models import Notifications
        try:
            self.group_name = 'tutor_group'
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            print('connected ')
            await self.accept()
        except Exception as e:
            print("Error in connect in admin notification", e)

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        except Exception as e:
            print("Error in disconnect admin notif:", e)

    async def receive(self, text_data):
        try:
            message = json.loads(text_data)
            print("admin_Received message:", message)
        except Exception as e:
            print("Error in receive admin noti:", e)

    async def create_tutor_notification(self, event):
        try:
            message = event['message']

            await self.send(json.dumps({

                'message': message,


            }))
        except Exception as e:
            print("Error in create admin notifications", e)


class StudentNotification(AsyncWebsocketConsumer):
    async def connect(self):
        from notifications.models import Notifications
        try:
            self.group_name = 'student_group'
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            print('connected ')
            await self.accept()
        except Exception as e:
            print("Error in connect in admin notification", e)

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        except Exception as e:
            print("Error in disconnect admin notif:", e)

    async def receive(self, text_data):
        try:
            message = json.loads(text_data)
            print("admin_Received message:", message)
        except Exception as e:
            print("Error in receive admin noti:", e)

    async def create_student_notification(self, event):
        try:
            message = event['message']

            await self.send(json.dumps({

                'message': message,


            }))
        except Exception as e:
            print("Error in create admin notifications", e)


class CommentUpdating(AsyncWebsocketConsumer):
    async def connect(self):
        from notifications.models import Notifications
        try:
            self.group_name = 'user_group'
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            print('connected ')
            await self.accept()
        except Exception as e:
            print("Error in connect in comment", e)

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        except Exception as e:
            print("Error in disconnect comment", e)

    async def receive(self, text_data):
        try:
            message = json.loads(text_data)
            print("comment message:", message)
        except Exception as e:
            print("Error in receive comment:", e)

    async def create_comment_update(self, event):
        try:
            message = event['message']

            await self.send(json.dumps({

                'message': message,


            }))
        except Exception as e:
            print("Error in create admin notifications", e)

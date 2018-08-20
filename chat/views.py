import logging
from django.contrib.auth import get_user_model
from .models import (
    ChatSession, ChatSessionMember, ChatSessionMessage, deserialize_user
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from notifications.signals import notify
from datetime import datetime, timedelta
# Create your views here.

# for logging
logger = logging.getLogger(__name__)


class ChatSessionView(APIView):
    """
    Manage Chat rooms(sessions).
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """
        Get all the chat room(session) that user created.
        """
        logger.info("Post request for creating chat room(session) !!!!!")

        user = request.user

        chat_sessions = ChatSession.objects.filter(owner=user)

        sessions = []
        for chat_session in chat_sessions.all():
            owner = chat_session.owner
            session = {}
            session['uri'] = chat_session.uri
            members = [
                deserialize_user(chat_session.user)
                for chat_session in chat_session.members.all()
            ]
            members.insert(0, deserialize_user(owner))  # Make the owner the first member
            session['members'] = members
            sessions.append(session)
        # sessions = [session.uri
        #             for session in chat_sessions.all()]

        return Response({
            'status': 'SUCCESS', 'sessions': sessions,
        })


    def post(self, request, *args, **kwargs):
        """
        Create a new chat room(session).
        """
        logger.info("Post request for creating chat room(session) !!!!!")

        user = request.user

        chat_session = ChatSession.objects.create(owner=user)

        return Response({
            'status': 'SUCCESS', 'uri': chat_session.uri,
            'message': 'New chat session created'
        })


class ChatSessionJoinView(APIView):
    """
    Join Chat rooms(sessions).
    """

    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        """
        Add a user to a chat rooms(sessions).
        """
        logger.info("Patch request for adding member into the chat room(session) !!!!!")
        logger.info("URI: {}, User: {} !!!!!".format(kwargs['uri'], request.data['username']))

        User = get_user_model()

        uri = kwargs['uri']
        username = request.data['username']
        user = User.objects.get(username=username)

        chat_session = ChatSession.objects.get(uri=uri)
        owner = chat_session.owner

        if owner != user:  # Only allow non owners join the room
            chat_session.members.get_or_create(
                user=user, chat_session=chat_session
            )

        owner = deserialize_user(owner)
        members = [
            deserialize_user(chat_session.user)
            for chat_session in chat_session.members.all()
        ]
        members.insert(0, owner)  # Make the owner the first member

        return Response({
            'status': 'SUCCESS', 'members': members,
            'message': '%s joined that chat' % user.username,
            'user': deserialize_user(user)
        })



class ChatSessionMessageView(APIView):
    """
    Post/Get Chat messages.
    """

    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        """
        Remove all messages in a chat session which has expired the given days.
        """
        logger.info("Delete request to remove chat messages @ room(session) : {}".format(kwargs['uri']))

        # uri = kwargs['uri']
        days = int(request.data['days'])
        ChatSessionMessage.objects.filter(create_date__gte=datetime.now() - timedelta(days=days)).delete()
        chat_session = ChatSession.objects.get(uri=uri)

        return Response({
            'id': chat_session.id, 'uri': chat_session.uri,
            'status': 'SUCCESS'
        })

    def get(self, request, *args, **kwargs):
        """
        return all messages in a chat session.
        """
        logger.info("Get request retrieve all the chat messages @ room(session) : {}".format(kwargs['uri']))

        uri = kwargs['uri']

        chat_session = ChatSession.objects.get(uri=uri)
        messages = [chat_session_message.to_json()
                    for chat_session_message in chat_session.messages.all()]

        return Response({
            'id': chat_session.id, 'uri': chat_session.uri,
            'messages': messages
        })

    def post(self, request, *args, **kwargs):
        """
        create a new message in a chat session.
        """
        logger.info("Post request send a new message @ room : {}".format(kwargs['uri']))
        logger.info("message : {}".format(request.data['message']))

        uri = kwargs['uri']
        message = request.data['message']

        user = request.user
        chat_session = ChatSession.objects.get(uri=uri)

        # ChatSessionMessage.objects.create(
        #     user=user, chat_session=chat_session, message=message
        # )
        chat_session_message = ChatSessionMessage.objects.create(
            user=user, chat_session=chat_session, message=message
        )
        notif_args = {
            'source': user,
            'source_display_name': user.get_full_name(),
            'category': 'chat', 'action': 'Sent',
            'obj': chat_session_message.id,
            'short_description': 'You a new message', 'silent': True,
            'extra_data': {
                'uri': chat_session.uri,
                'message': chat_session_message.to_json()
            }
        }
        notify.send(
            sender=self.__class__, **notif_args, channels=['websocket']
        )

        return Response({
            'status': 'SUCCESS', 'uri': chat_session.uri, 'message': message,
            'user': deserialize_user(user)
        })
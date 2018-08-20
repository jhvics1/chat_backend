from django.db import models
from django.contrib.auth import get_user_model
from uuid import uuid4
import logging

# Create your models here.

# for logging
logger = logging.getLogger(__name__)

User = get_user_model()


def deserialize_user(user):
    """
    Deserialize user instance to JSON.
    """
    return {
        'id': user.id, 'username': user.username, 'email': user.email,
        'first_name': user.first_name, 'last_name': user.last_name
    }


def _generate_unique_uri():
    """
    Generates a unique uri for the chat session.
    """
    return str(uuid4()).replace('-', '')[:15]


class TrackableDateModel(models.Model):
    """
    Abstract model to Track the creation/updated date for a model.
    """
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ChatSession(TrackableDateModel):
    """
    A Chat Session.
    The uri's are generated by taking the first 15 characters from a UUID
    """
    # for logging
    logger.info("ChatSession Called~~~~~~!!!!!")
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    uri = models.URLField(default=_generate_unique_uri)


class ChatSessionMessage(TrackableDateModel):
    """
    Messages for a session.
    """
    logger.info("ChatSessionMessage Called~~~~~~!!!!!")
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    chat_session = models.ForeignKey(
        ChatSession, related_name='messages', on_delete=models.PROTECT
    )
    message = models.TextField(max_length=2000)

    def to_json(self):
        """deserialize message to JSON."""
        return {'user': deserialize_user(self.user), 'message': self.message}


class ChatSessionMember(TrackableDateModel):
    """
    All the users in a chat session.
    """
    logger.info("ChatSessionMember Called~~~~~~!!!!!")
    chat_session = models.ForeignKey(
        ChatSession, related_name='members', on_delete=models.PROTECT
    )
    user = models.ForeignKey(User, on_delete=models.PROTECT)
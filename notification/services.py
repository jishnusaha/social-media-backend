# notifications/services.py
from django.contrib.contenttypes.models import ContentType
from .models import Notification


class NotificationService:
    @staticmethod
    def create_notification(
        recipient,
        notification_type,
        title,
        message=None,
        actor=None,
        content_object=None,
        extra_data=None,
    ):
        """
        Create a notification for a user

        Args:
            recipient: The EndUser receiving the notification
            notification_type: Type from Notification.NotificationType
            title: Title of the notification
            message: Optional message content
            actor: Optional EndUser who triggered the notification
            content_object: Optional related object (post, comment, etc.)
            extra_data: Optional JSON data for additional context

        Returns:
            Notification object
        """
        if not message:
            message = title

        notification = Notification(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            actor=actor,
            extra_data=extra_data,
        )

        if content_object:
            content_type = ContentType.objects.get_for_model(content_object)
            notification.content_type = content_type
            notification.object_id = content_object.id

        notification.save()
        return notification

    @staticmethod
    def create_friend_request_notification(recipient, sender, friend_request):
        """Create a notification for a new friend request"""
        title = f"{sender.get_full_name() or sender.username} sent you a friend request"
        return NotificationService.create_notification(
            recipient=recipient,
            notification_type=Notification.NotificationType.FRIEND_REQUEST,
            title=title,
            actor=sender,
            content_object=friend_request,
        )

    @staticmethod
    def create_friend_accept_notification(recipient, acceptor, friendship):
        """Create a notification for an accepted friend request"""
        title = f"{acceptor.get_full_name() or acceptor.username} accepted your friend request"
        return NotificationService.create_notification(
            recipient=recipient,
            notification_type=Notification.NotificationType.FRIEND_ACCEPT,
            title=title,
            actor=acceptor,
            content_object=friendship,
        )

    @staticmethod
    def create_post_reaction_notification(post_author, reactor, post, reaction_type):
        """Create a notification for a reaction on a post"""
        reaction_text = reaction_type.lower()
        title = f"{reactor.get_full_name() or reactor.username} reacted with {reaction_text} to your post"

        # Don't notify yourself
        if post_author.id == reactor.id:
            return None

        return NotificationService.create_notification(
            recipient=post_author,
            notification_type=Notification.NotificationType.POST_LIKE,
            title=title,
            actor=reactor,
            content_object=post,
            extra_data={"reaction_type": reaction_type},
        )

    @staticmethod
    def create_post_comment_notification(post_author, commenter, post, comment):
        """Create a notification for a comment on a post"""
        title = (
            f"{commenter.get_full_name() or commenter.username} commented on your post"
        )

        # Don't notify yourself
        if post_author.id == commenter.id:
            return None

        return NotificationService.create_notification(
            recipient=post_author,
            notification_type=Notification.NotificationType.POST_COMMENT,
            title=title,
            message=f"{commenter.get_full_name() or commenter.username} commented: '{comment.content[:50]}...' on your post",
            actor=commenter,
            content_object=comment,
            extra_data={"post_id": str(post.id)},
        )

    @staticmethod
    def create_comment_reply_notification(parent_comment_author, replier, post, reply):
        """Create a notification for a reply to a comment"""
        title = f"{replier.get_full_name() or replier.username} replied to your comment"

        # Don't notify yourself
        if parent_comment_author.id == replier.id:
            return None

        return NotificationService.create_notification(
            recipient=parent_comment_author,
            notification_type=Notification.NotificationType.COMMENT_REPLY,
            title=title,
            message=f"{replier.get_full_name() or replier.username} replied: '{reply.content[:50]}...' to your comment",
            actor=replier,
            content_object=reply,
            extra_data={"post_id": str(post.id)},
        )

    @staticmethod
    def create_new_message_notification(recipient, sender, conversation, message):
        """Create a notification for a new message"""
        if conversation.is_group and conversation.name:
            title = f"New message in {conversation.name}"
        else:
            title = f"New message from {sender.get_full_name() or sender.username}"

        # Don't notify yourself
        if recipient.id == sender.id:
            return None

        return NotificationService.create_notification(
            recipient=recipient,
            notification_type=Notification.NotificationType.MESSAGE,
            title=title,
            message=f"{sender.get_full_name() or sender.username}: {message.content[:50]}{'...' if len(message.content) > 50 else ''}",
            actor=sender,
            content_object=message,
            extra_data={"conversation_id": str(conversation.id)},
        )

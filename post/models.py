from common.base_models import DataBaseModels
from django.db import models
from users.models import Users


class Post(DataBaseModels):
    """
    Model representing a post created by a user.

    Fields:
    - user: Foreign key to the Users model representing the author of the post.
    - content: Text field for the content of the post.
    - image: ImageField for uploading images associated with the post.
    - video: FileField for uploading videos associated with the post.
    """
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(null=True)
    image = models.ImageField(upload_to="post_images/", null=True, blank=True)
    video = models.FileField(upload_to="post_vidoes/", null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.user.username} - posts"


class Comment(DataBaseModels):
    """
    Model representing a comment on a post.

    Fields:
    - user: Foreign key to the Users model representing the author of the comment.
    - post: Foreign key to the Post model representing the post being commented on.
    - parent: Optional foreign key to another Comment, allowing for nested replies.
    - content: Text field for the content of the comment.
    """
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    content = models.TextField(null=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.user.username} - comment"


class Like(DataBaseModels):
    """
    Model representing a like on a post by a user.

    Fields:
    - user: Foreign key to the Users model representing the user who liked the post.
    - post: Foreign key to the Post model representing the post that was liked.
    """
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")

    class Meta:
        unique_together = ("user", "post")

    def __str__(self) -> str:
        return f"Like by {self.user.username} on {self.post.content[:10]} post"

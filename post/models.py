from common.base_models import DataBaseModels
from django.db import models
from users.models import Users


class Post(DataBaseModels):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(null=True)
    image = models.ImageField(upload_to="post_images/", null=True, blank=True)
    video = models.FileField(upload_to="post_vidoes/", null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.user.username} - posts"


class Comment(DataBaseModels):
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
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")

    class Meta:
        unique_together = ("user", "post")

    def __str__(self) -> str:
        return f"Like by {self.user.username} on {self.post.content[:10]} post"

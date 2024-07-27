from django.urls import path
from .views import PostViewSet, CommentViewSet, LikeViewSet

handle_like = PostViewSet.as_view({
    'post': 'like'
})

add_comment = PostViewSet.as_view({
    'post': 'comment'
})

urlpatterns = [
    path("post", PostViewSet.as_view({'get':'list','post':'create'}), name="post"),
    path("post/<int:id>", PostViewSet.as_view({'get':'retrieve','put':'update','delete':'destroy'}), name="posts"),
    path("like/<int:id>", handle_like, name="like"),
    path("add_comment/<int:id>", add_comment, name="add_comment"),

    # path("comment", CommentViewSet.as_view({'get':'list','post':'create'}), name="comment"),
    # path("comment/<int:id>", CommentViewSet.as_view({'get':'retrieve','put':'update','delete':'destroy'}), name="comments"),
    path("list_like", LikeViewSet.as_view({'get':'list'}), name="list_like"),
    # path("like/<int:id>", LikeViewSet.as_view({'get':'retrieve','put':'update','delete':'destroy'}), name="likes")
]

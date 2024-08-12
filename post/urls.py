from django.urls import path

from .views import AcademyDashBoard, PlayerHomePageView, PostViewSet

handle_like = PostViewSet.as_view({"post": "like"})

add_comment = PostViewSet.as_view({"post": "comment"})

urlpatterns = [
    path("post", PostViewSet.as_view({"get": "list", "post": "create"}), name="post"),
    path(
        "post/<int:id>",
        PostViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "delete": "destroy",
                "patch": "partial_update",
            }
        ),
        name="posts",
    ),
    path("like/<int:id>", handle_like, name="like"),
    path("add_comment/<int:id>", add_comment, name="add_comment"),
    path("home", PlayerHomePageView.as_view(), name="home"),
    path("academy_dashboard", AcademyDashBoard.as_view(), name="academy_dashboard"),
]

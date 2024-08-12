from django.urls import path

from .views import (AcademyManage, AccountsView, DashboardViewSet,
                    PlayerManage, ToggleActive, ToggleIsCertified)

urlpatterns = [
    path("list_academy", AcademyManage.as_view(), name="list_academy"),
    path(
        "update_certified/<int:id>",
        ToggleIsCertified.as_view(),
        name="update_certified",
    ),
    path("list_players", PlayerManage.as_view(), name="list_player"),
    path(
        "toggleIsactive/<int:id>",
          ToggleActive.as_view(),
            name="toggleIsactive"
    ),
    path("dashboard", DashboardViewSet.as_view(), name="dashboard"),
    path("payment_details", AccountsView.as_view(), name="payment_details"),
]

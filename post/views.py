from datetime import timedelta

from django.db.models import Count, F, Q, Sum
from django.utils import timezone
from rest_framework import response, status, views, viewsets
from rest_framework.decorators import action
from selection_trial.models import PlayersInTrial, Trial
from user_profile.models import Achievements, Follow
from users.models import Sport, UserProfile, Users

from .models import Comment, Like, Post
from .serializers import CommentSerializer, PostSerializer


class PostViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing posts.
    """
    queryset = Post.objects.all().select_related("user__userprofile")
    serializer_class = PostSerializer
    lookup_field = "id"

    def get_queryset(self):
        """
        Return a queryset of posts filtered by user ID or the current user.
        """
        profile_id = self.request.GET.get("id", None)
        if profile_id and profile_id != "undefined" and profile_id != "null":
            return (
                Post.objects.filter(user=profile_id)
                .select_related("user__userprofile")
                .prefetch_related("likes")
                .order_by("-id")
            )

        return (
            Post.objects.filter(user=self.request.user)
            .select_related("user__userprofile")
            .prefetch_related("likes")
            .order_by("-id")
        )

    def retrieve(self, request, id):
        """
        Return a queryset of posts filtered by profile ID or the current user.
        """
        if Post.objects.filter(id=id).exists():
            post = (
                Post.objects.filter(id=id)
                .select_related("user__userprofile")
                .prefetch_related("likes")
                .first()
            )
        else:
            return response.Response(
                data="post not found", status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(post)
        return response.Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def like(self, request, id=None):
        """
        Return a queryset of posts filtered by profile ID or the current user.
        """
        try:
            post = Post.objects.get(id=id)
            user = request.user
            if Like.objects.filter(user=user, post=post).exists():
                like = Like.objects.get(user=user, post=post)
                like.delete()
                return response.Response(
                    {"status": "unliked"}, status=status.HTTP_200_OK
                )

            Like.objects.create(user=user, post=post)
            return response.Response(
                {"status": "liked"}, status=status.HTTP_201_CREATED
            )

        except Exception as e:
            print(e, "some error in liking")
            return response.Response(
                {"message": "No post found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=["POST"])
    def comment(self, request, id=None):
        """
        Comment on a specific Post. Supports replies to existing comments.
        """
        try:
            post = Post.objects.get(id=id)
            parent_id = request.data.get("parent", None)
            parent = None
            if (
                parent_id
            ):  # if the comment is reply of a comment then store the commnet as parent
                try:
                    parent = Comment.objects.get(id=parent_id, post=post)
                except Comment.DoesNotExist:
                    return response.Response(
                        data="commment not found to reply",
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, post=post, parent=parent)
                return response.Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return response.Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            print(e, "error commenting")
            return response.Response(data=f"{str(e)}", status=status.HTTP_404_NOT_FOUND)


class PlayerHomePageView(views.APIView):
    """
    A view to retrieve the homepage data for a player, including posts, trials, and top academies.
    """
    def get(self, request):
        user = request.user
        page = int(request.query_params.get("page", 1))
        posts_per_page = 10
        user_sports = Sport.objects.filter(user=user).values_list(
            "sport_name", flat=True
        )
        try:
            user_profile = UserProfile.objects.get(user=user)
            user_state = user_profile.state
            user_district = user_profile.district
        except UserProfile.DoesNotExist:
            user_district = None
            user_state = None

        friend_ids = user.friends.values_list("id", flat=True)
        followed_academy_ids = Follow.objects.filter(player=user).values_list(
            "academy__id", flat=True
        )

        personal_posts = Post.objects.filter(
            Q(user=user) | Q(user__in=friend_ids) | Q(user__in=followed_academy_ids)
        )

        if personal_posts.count() < posts_per_page:
            last_week = timezone.now() - timedelta(days=7)
            recommended_posts = (
                Post.objects.filter(created_at__gte=last_week)
                .exclude(id__in=personal_posts)
                .annotate(engagement=Count("likes") + Count("comments"))
                .order_by("-engagement")
            )

            if user_sports:
                recommended_posts = recommended_posts.filter(
                    Q(user__sport__sport_name__in=user_sports)
                    | Q(user__userprofile__state=user_state)
                    | Q(user__userprofile__district=user_district)
                )

            posts = (
                (personal_posts | recommended_posts).distinct().order_by("-created_at")
            )
        else:
            posts = personal_posts.distinct().order_by("-created_at")

        # Pagination
        start = 0
        end = ((page - 1) * posts_per_page) + posts_per_page
        paginated_posts = posts[start:end]

        post_serializer = PostSerializer(
            paginated_posts, many=True, context={"request": request}
        )

        # User detials for homepage
        user_details = {
            "username": user.username,
            "friends_count": user.friends.all().count(),
            "bio": user.userprofile.bio,
            "post_count": Post.objects.filter(user=user).count(),
            "achievements_count": Achievements.objects.filter(user=user).count(),
            "id": user.id,
        }

        top_academies = (
            Users.objects.filter(is_academy=True, is_verified=True, is_staff=False)
            .annotate(followers_count=Count("followers"))
            .order_by("-followers_count")
            .values(
                "username",
                "followers_count",
                "userprofile__state",
                "userprofile__district",
                "userprofile__profile_photo",
                "id",
            )[:3]
        )

        today = timezone.now()
        trials = (
            Trial.objects.filter(
                Q(deadline__gte=today)
                & Q(is_active=True)
                & (
                    Q(academy__id__in=followed_academy_ids)
                    | Q(sport__in=user_sports)
                    | Q(district=user_district)
                )
            )
            .order_by("deadline")[:3]
            .values("name", "state", "district", "image", "id")
        )

        if trials.count() < 3:
            additional_trials = (
                Trial.objects.filter(deadline__gte=today, is_active=True)
                .exclude(id__in=trials.values_list("id", flat=True))
                .order_by("deadline")[: 3 - trials.count()]
                .values("name", "state", "district", "image", "id")
            )
            trials = list(trials) + list(additional_trials)

        return response.Response(
            {
                "posts": post_serializer.data,
                "has_more": posts.count() > end,
                "page": page + 1,
                "user": user_details,
                "trials": trials,
                "academies": top_academies,
            },
            status=status.HTTP_200_OK,
        )


class AcademyDashBoard(views.APIView):
    """
    A view to retrieve the dashboard data for an academy.
    """
    def get(self, request):
        academy = request.user
        today = timezone.now()

        # Trial statistics
        total_trials = Trial.objects.filter(academy=academy).count()
        completed_trials = Trial.objects.filter(
            academy=academy, is_active=True, trial_date__lt=today
        ).count()
        upcoming_trials_count = Trial.objects.filter(
            academy=academy, trial_date__gte=today, is_active=True
        ).count()
        cancelled_trails = Trial.objects.filter(
            academy=academy, is_active=False
        ).count()

        # Followers and post interactions
        followers = Follow.objects.filter(academy=academy).count()

        posts = Post.objects.filter(user=academy)
        likes_count = Like.objects.filter(post__in=posts).count()
        comments_count = Comment.objects.filter(post__in=posts).count()
        total_interactions = likes_count + comments_count

        upcoming_trials = (
            Trial.objects.filter(academy=academy, trial_date__gte=today)
            .order_by("trial_date")[:5]
            .values(
                "name",
                "trial_date",
                "sport",
                "is_registration_fee",
                "registration_fee",
                "id",
            )
        )

        popular_posts = (
            Post.objects.filter(user=academy)
            .annotate(likes_count=Count("likes"))
            .order_by("-likes_count")[:5]
            .values("content", "likes_count", "id")
        )

        total_participants = PlayersInTrial.objects.filter(
            trial__academy=academy
        ).count()

        total_received_amount = (
            PlayersInTrial.objects.filter(
                trial__academy=academy,
                payment_status="confirmed",
                trial__is_active=True,
            ).aggregate(total=Sum("trial__registration_fee"))["total"]
            or 0
        )

        recent_payments = (
            PlayersInTrial.objects.filter(
                trial__academy=academy,
                payment_status="confirmed",
                trial__is_active=True,
            )
            .annotate(
                player__username=F("player__username"),
                trial__name=F("trial__name"),
                payment_amount=F("trial__registration_fee"),
                payment_date=F("created_at"),
                tr_id=F("trial__id"),
                pl_id=F("player__id"),
            )
            .values(
                "player__username",
                "trial__name",
                "payment_amount",
                "payment_date",
                "tr_id",
                "pl_id",
            )
            .order_by("-created_at")[:6]
        )

        dashboard_data = {
            "stats": {
                "totalTrials": total_trials,
                "completedTrials": completed_trials,
                "upcomingTrials": upcoming_trials_count,
                "cancelledTrials": cancelled_trails,
            },
            "recentTrials": list(upcoming_trials),
            "popularPosts": list(popular_posts),
            "playerEngagement": {
                "followers": followers,
                "trialParticipants": total_participants,
                "postInteractions": total_interactions,
            },
            "upcomingTrials": list(upcoming_trials),
            "payments": {
                "totalReceived": total_received_amount,
                "recentPayments": recent_payments,
            },
        }

        return response.Response(dashboard_data)

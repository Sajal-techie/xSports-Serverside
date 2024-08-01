from rest_framework import viewsets, response, status, views
from rest_framework.decorators import action
from django.db.models import Q,Count
from django.utils import timezone
from datetime import timedelta
from selection_trial.models import Trial
from selection_trial.serializers import TrialSerializer
from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer, LikeSerializer
from users.models import  Users, UserProfile, Sport
from user_profile.models import FriendRequest, Follow,Achievements

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().select_related('user__userprofile')
    serializer_class = PostSerializer
    lookup_field = 'id'

    def get_queryset(self):
        profile_id = self.request.GET.get('id',None)
        print(self, self.request.GET,profile_id,'getqeuryset')
        if profile_id and profile_id != 'undefined' and profile_id != 'null':
            print(Post.objects.filter(user=profile_id))
            return Post.objects.filter(user=profile_id).select_related('user__userprofile').prefetch_related('likes').order_by('-id')
        
        return Post.objects.filter(user=self.request.user).select_related('user__userprofile').prefetch_related('likes').order_by('-id')

    def retrieve(self, request,id, *args, **kwargs):
        print(args,kwargs,'in retireve',id)
        if Post.objects.filter(id=id).exists():
            post = Post.objects.filter(id=id).select_related('user__userprofile').prefetch_related('likes').first()
        else:
            return response.Response(data="post not found", status=status.HTTP_404_NOT_FOUND) 
        
        serializer = self.get_serializer(post)
        return response.Response(serializer.data,status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def like(self, request, id=None):
        print(id, 'id of post',request.user)

        try:
            post = Post.objects.get(id=id)
            user = request.user
            print(post,'post')
            like, created = Like.objects.get_or_create(user=user, post=post)
            print(like, created,'created')
            
            if not created:
                like.delete()
                return response.Response({'status':'unliked'}, status=status.HTTP_200_OK)
            
            return response.Response({'status':'liked'}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            print(e,'some error in liking')
            return response.Response({'message':'No post found'}, status=status.HTTP_404_NOT_FOUND)


    @action(detail=True, methods=['POST'])
    def comment(self, request, id=None):
        try:
            print(request.data, request.user,id,'in commnet view')
            post = Post.objects.get(id=id)
            parent_id = request.data.get('parent',None) 
            parent = None
            if parent_id:    # if the comment is reply of another comment then store the commnet as parent
                try:
                    parent = Comment.objects.get(id=parent_id, post=post)
                except Comment.DoesNotExist:
                    return response.Response(data="commment not found to reply", status=status.HTTP_400_BAD_REQUEST)
                
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, post=post, parent=parent)
                return response.Response(serializer.data, status=status.HTTP_201_CREATED)
            print(serializer.errors,'serializer erors')
            return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print(e,'error in comment')
            return response.Response(data=f'{str(e)}',status=status.HTTP_404_NOT_FOUND)



class HomePageView(views.APIView):
    def get(self, request, *args, **kwargs):
        user = request.user
        page = int(request.query_params.get('page', 1))
        posts_per_page = 10
        user_sports = Sport.objects.filter(user=user).values_list('sport_name', flat=True)
        print(page,'pagenumber')
        try:
            user_profile = UserProfile.objects.get(user=user)
            user_state = user_profile.state
            user_district = user_profile.district
        except UserProfile.DoesNotExist:
            user_district = None
            user_state = None

        friend_ids = user.friends.values_list('id', flat=True)
        followed_academy_ids = Follow.objects.filter(player=user).values_list('academy__id', flat=True)

        personal_posts = Post.objects.filter(
            Q(user=user) |
            Q(user__in=friend_ids) |
            Q(user__in=followed_academy_ids)
        )

        if personal_posts.count() < posts_per_page:
            last_week = timezone.now() - timedelta(days=7)
            recommended_posts = Post.objects.filter(
                created_at__gte=last_week
            ).exclude(
                id__in=personal_posts
            ).annotate(
                engagement=Count('likes') + Count('comments')
            ).order_by('-engagement')

            if user_sports:
                recommended_posts = recommended_posts.filter(
                    Q(user__sport__sport_name__in=user_sports) |
                    Q(user__userprofile__state=user_state) |
                    Q(user__userprofile__district=user_district)
                )

            posts = (personal_posts | recommended_posts).distinct().order_by('-created_at')
        else:
            posts = personal_posts.distinct().order_by('-created_at')

        start = 0
        end = ((page - 1) * posts_per_page) + posts_per_page
        paginated_posts = posts[start:end]

        post_serializer = PostSerializer(paginated_posts, many=True, context={'request': request})

        # to show user detials in home page
        user_details = {
            'username':user.username,
            'friends_count' : user.friends.all().count(),
            'bio' : user.userprofile.bio,
            'post_count': Post.objects.filter(user=user).count(),
            'achievements_count': Achievements.objects.filter(user=user).count(),
            'id':user.id
        } 

        top_academies = Users.objects.filter(
            is_academy=True,
            is_verified=True,
            is_staff=False
            ).annotate(
                followers_count=Count('followers')
                ).order_by('-followers_count'
                           ).values(
                               'username',
                               'followers_count',
                               'userprofile__state',
                               'userprofile__district',
                               'userprofile__profile_photo',
                               'id'
                               )[:3]

        today = timezone.now()
        trials = Trial.objects.filter(
            Q(deadline__gte=today) &
            Q(is_active=True) &
            (
                Q(academy__id__in=followed_academy_ids) |
                Q(sport__in=user_sports) |
                Q(district=user_district)
            )
        ).order_by('deadline')[:3]

        if trials.count() < 3:
            additional_trials = Trial.objects.filter(
                deadline__gte=today,
                is_active=True
            ).exclude(
                id__in=trials.values_list('id', flat=True)
            ).order_by('deadline')[:3 - trials.count()]
            trials = list(trials) + list(additional_trials)

        trial_details = trials.values('name', 'state', 'district', 'image','id')


        return response.Response({
            'posts': post_serializer.data,
            'has_more': posts.count() > end,
            'page': page+1,
            'user':user_details,
            'trials':trial_details,
            'academies':top_academies
        }, status=status.HTTP_200_OK)
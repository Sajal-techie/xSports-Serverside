from rest_framework import viewsets, response, status
from rest_framework.decorators import action
from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer, LikeSerializer


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


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        print(self.request.user, ' in coment get query set')
        return super().get_queryset()

    def perform_create(self, serializer):
        print(self.request.user, serializer, 'in perfomr create')
        return super().perform_create(serializer)
    

class LikeViewSet(viewsets.ModelViewSet):
    serializer_class = LikeSerializer

    def get_queryset(self):
        print(self.request.user)
        return super().get_queryset()

    def perform_create(self, serializer):
        print(self.request.user, serializer, 'perfomr create')
        return super().perform_create(serializer)
    
    def destroy(self, request, *args, **kwargs):
        print(request.user, args, kwargs ,' delete like')
        return super().destroy(request, *args, **kwargs)
from ast import Not
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
# from django.views.decorators.cache import cache_page
from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post, User


def index(request):
    template = 'posts/index.html'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.POSTS_NUMBER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': 'Это главная страници проекта Yatube',
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, settings.POSTS_NUMBER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    user_object = get_object_or_404(User, username=username)
    post_list = user_object.posts.all()
    post_count = post_list.count()
    paginator = Paginator(post_list, settings.POSTS_NUMBER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/profile.html'
    following = False
    if request.user.username:
        following = Follow.objects.filter(
            user=request.user,
            author=User.objects.get(username=username)
        ).exists()
    context = {
        'page_obj': page_obj,
        'post_count': post_count,
        'author': user_object,
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_count = post.author.posts.count()
    template = 'posts/post_detail.html'
    form = CommentForm()
    context = {
        'post_count': post_count,
        'post': post,
        'form': form,
        'comments': post.comments.all()
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    if request.method != 'POST':
        form = PostForm()
        return render(request, template, {'form': form})
    form = PostForm(request.POST, files=request.FILES or None)
    username = request.user.username
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', username=username)
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.id)
    if request.method != 'POST':
        form = PostForm(instance=post)
        template = 'posts/create_post.html'
        return render(request, template, {
            'form': form,
            'is_edit': True,
            'post': post}
        )
    form = PostForm(
        request.POST,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.id)
    template = 'posts/create_post.html'
    return render(request, template, {
        'form': form,
        'is_edit': True,
        'post': post}
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    list_folower = request.user.follower.all()
    list_author = []
    for item in list_folower:
        list_author.append(item.author)
    post_list = Post.objects.filter(author__in=list_author)
    paginator = Paginator(post_list, settings.POSTS_NUMBER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/follow_index.html'
    context = {
        'title': 'Избранные авторы',
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    a = request.user.username != username
    b = Not (Follow.objects.get(
        user=request.user,
        author=User.objects.get(username=username)
        ).exists())
    if a and b:
        Follow.objects.create(
            user=request.user,
            author=User.objects.get(username=username)
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user,
        author=User.objects.get(username=username)
    ).delete()
    return redirect('posts:profile', username=username)

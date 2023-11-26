from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.checks import Tags
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from taggit.models import Tag

from .forms import PostForm, CommentForm, CustomUserCreationForm, UserProfileForm, UserForm, SearchForm
from .models import User, Post, UserProfile, Contact, Comment, Bookmarks, Notification
import psycopg2
import json


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        user_profile_form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid() and user_profile_form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            photo = user_profile_form.cleaned_data['profile_image'] if user_profile_form.cleaned_data['profile_image'] else 'profile_images/avatar.jpg'
            password1 = form.cleaned_data['password1']
            try:
                user = User.objects.create_user(username, email=email, password=password1)
                user.save()
                UserProfile.objects.create(
                    user=user,
                    profile_image=photo
                )
            except IntegrityError:
                return render(request, "network/register.html", {
                    "message": "Username already taken."
                })
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
    else:
        form = CustomUserCreationForm()
        user_profile_form = UserProfileForm()
    return render(request, "network/register.html", {"user_form": form, "user_profile_form": user_profile_form})


@login_required
def new_post(request):
    if request.method == 'POST':
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            post = post_form.save(commit=False)
            post.author = request.user
            post_form.save()
            return redirect(reverse('index'))
    else:
        post_form = PostForm()
    return render(request, 'network/create_post.html', {'post_form': post_form})

# class AddNewPostView(CreateView):
#     model = Post
#     template_name = 'network/create_post.html'
#     fields = ['full_name', 'phone_number']
#     success_url = reverse_lazy('patient_list')
#
#     def form_valid(self, form):
#         form.instance.date_reg = timezone.now()
#         return super().form_valid(form)


class PostListView(LoginRequiredMixin, ListView):
    paginate_by = 3
    model = Post
    template_name = 'network/index.html'

    def get_queryset(self):
        posts = Post.objects.all()
        search_query = self.request.GET.get('query', False)
        if search_query:
            posts = posts.filter(text__icontains=search_query)

        if self.kwargs:
            tag = get_object_or_404(Tag, slug=self.kwargs['tag_slug'])
            posts = posts.filter(tags__in=[tag])
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.annotate(post_count=Count('post')).filter(post_count__gt=0)
        context['bookmarks'] = Bookmarks.objects.filter(user=self.request.user).values_list('post', flat=True)
        self.request.session['unread_notifications'] = Notification.objects.filter(
            user=self.request.user, is_seen=False).count()  # I will change it to django channels
        return context


@login_required()
def explore(request):
    tags = Tag.objects.annotate(post_count=Count('post')).filter(post_count__gt=0)
    search_form = SearchForm()
    qs_json = json.dumps(list(set((Post.objects.values_list('text', flat=True).exclude(text='')))))
    return render(request, 'network/explore_page.html', {'tags': tags, 'search_form': search_form, 'qs_json': qs_json})


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template = 'network/post_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        post = self.get_object()
        context['comments'] = Comment.objects.filter(auction=post)
        return context

    def post(self, request, *args, **kwargs):
        post = self.get_object()
        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.auction = post
            new_comment.commenter = request.user
            new_comment.save()
            if request.user != post.author:
                Notification.objects.create(user=post.author, message=f"User '{request.user}' commented on your post")

        return redirect('post_detail', pk=post.pk)


@login_required
def user_profile(request, slug):
    user = get_object_or_404(User, username=slug)
    posts = Post.objects.filter(author=user)
    profile = get_object_or_404(UserProfile, user=user)
    request.session['unread_notifications'] = Notification.objects.filter(user=request.user, is_seen=False).count()
    return render(request, 'network/user_profile.html',
                  {'profile': profile, 'posts': posts})


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'network/user_profile_edit.html'

    def get_object(self, queryset=None):
        return self.request.user.userprofile

    def get(self, request, *args, **kwargs):
        user_profile = UserProfileForm(instance=request.user.userprofile)
        user_form = UserForm(instance=request.user)

        context = {
            'user_form': user_form,
            'profile_form': user_profile
        }

        return render(request, 'network/user_profile_edit.html', context)

    def post(self, request, *args, **kwargs):
        user_profile = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        user_form = UserForm(request.POST, instance=request.user)
        if user_profile.is_valid() and user_form.is_valid():
            user_profile.save()
            user_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            self.object = self.get_object()
            return HttpResponseRedirect(reverse('user_profile', kwargs={'slug': self.object.user.username}))
        else:
            context = {
                'user_form': user_form,
                'profile_form': user_profile
            }
            messages.error(request, 'Error updating you profile')

            return render(request, 'network/user_profile_edit.html', context)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'network/post_edit.html'

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        post_user = post.author
        if request.user == post_user:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponseForbidden("Access denied")


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'network/post_delete.html'

    def get_success_url(self):
        return reverse('user_profile', kwargs={'slug': self.object.author})

    def form_valid(self, form):
        messages.success(self.request, "The post was deleted successfully.")
        return super().form_valid(form)


@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')  # data-id
    action = request.POST.get('action')  # data-action
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(
                    user_from=request.user,
                    user_to=user)
                Notification.objects.create(user=user, message=f"User '{request.user}' subscribed to you")
            else:
                Contact.objects.filter(user_from=request.user,
                                       user_to=user).delete()
                Notification.objects.create(user=user, message=f"User '{request.user}' unsubscribed from you")
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status':'error'})
    return JsonResponse({'status':'error'})


@login_required
@require_POST
def likes(request):
    post_id = request.POST.get('id')
    action = request.POST.get('action')
    if post_id and action:
        try:
            post = Post.objects.get(pk=post_id)
            if action == 'like':
                post.like.add(request.user)
                if post.author != request.user:
                    Notification.objects.create(user=post.author, message=f"User '{request.user}' liked your post")
            else:
                post.like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Post.DoesNotExist:
            print("Post doesn't exist.")
    return JsonResponse({'status': 'error'})


class FollowingListView(LoginRequiredMixin, ListView):
    paginate_by = 3
    model = Post
    template_name = 'network/index.html'

    def get_queryset(self):
        monitoring_users = Contact.objects.filter(user_from=self.request.user).values('user_to')
        posts = Post.objects.filter(author__in=monitoring_users)
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.annotate(post_count=Count('post')).filter(post_count__gt=0)
        return context


class BookmarksListView(LoginRequiredMixin, ListView):
    paginate_by = 3
    model = Post
    template_name = 'network/bookmarks.html'

    def get_queryset(self):
        favourites = Bookmarks.objects.filter(user=self.request.user).values_list('post__pk')
        return Post.objects.filter(pk__in=favourites)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.annotate(post_count=Count('post')).filter(post_count__gt=0)
        context['bookmarks'] = Bookmarks.objects.filter(user=self.request.user).values_list('post', flat=True)
        return context

    def post(self, request, *args, **kwargs):
        post_id = request.POST.get('id')
        action = request.POST.get('action')
        if post_id and action:
            try:
                post = get_object_or_404(Post, pk=post_id)
                bookmarks = Bookmarks.objects.filter(post=post, user=request.user).first()
                if action == 'add':
                    bookmarks = Bookmarks.objects.create(user=request.user)
                    bookmarks.post.add(post)
                elif action == 'delete':
                    bookmarks.delete()
                return JsonResponse({'status': 'ok'})
            except Post.DoesNotExist:
                print("Post doesn't exist.")
        return JsonResponse({'status': 'error'})


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'network/notifications.html'

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-timestamp")

    def put(self, request, *args, **kwargs):
        Notification.objects.filter(user=request.user).update(is_seen=True)
        return JsonResponse({'status': 'success'})



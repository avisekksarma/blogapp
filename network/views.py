import json
import os
from django.core.files import File
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect,HttpResponseNotAllowed,JsonResponse
from django.shortcuts import render,redirect
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from django.db.utils import OperationalError
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .forms import UserRegisterform
from .models import User,NewPost

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
filehandler = logging.FileHandler('views_log.log')
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(lineno)d:%(name)s:%(message)s')
filehandler.setFormatter(formatter)
logger.addHandler(filehandler)


@ensure_csrf_cookie
def index(request):
    if request.method=="POST" and request.POST['post-content']:
        if not request.user.is_authenticated:
            return redirect('login')

        post_content = request.POST['post-content']
        print(type(request.user))
        print(request.user)
        if post_content != '':
            NewPost.objects.create(author=request.user,content=post_content)
            messages.success(request,'New Post was published successfully !!!')  
        else:
            messages.error(request,'You must enter something in the post box.')
        return HttpResponseRedirect(reverse('index'))
    
    if request.method == "PUT":
        data = json.loads(request.body)
        id = int(data['id'])
        post = NewPost.objects.get(pk=id)
        if post.author == request.user:
            # change the content as this is legit request
            post.content = data['content']
            post.save()

            return JsonResponse({"success": "Successfully updated content of the post."
            ,'new_content': post.content}, status=200)
        else:
            return JsonResponse({"error": "This request is not legit request."}, status=404)
    
    # get request section
    posts = NewPost.objects.all()
    posts = posts.order_by('-created_time','-id')
    # pagination section
    paginator = Paginator(posts,3)
    page_number = request.GET.get('page',1)
    page_obj = paginator.page(page_number)


    if request.user.is_authenticated: 
        liked_posts = request.user.liked_posts.all()
    else:
        liked_posts = []
    context ={
        'all_posts': page_obj.object_list,
        'liked_posts': liked_posts,
        'page_obj':page_obj,
        'page_number':page_number
    }
    return render(request, "network/index.html",context)


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
    return HttpResponseRedirect(reverse("index"))


def register(request):
    
    if request.method == "POST":
        registerform = UserRegisterform(request.POST,request.FILES)
        if registerform.is_valid():
            new_user = registerform.save()
            username = new_user.username
            messages.success(request,f'Account created for {username}!!!')
            return HttpResponseRedirect(reverse('login'))
    else:
        registerform = UserRegisterform()
    context ={
        'form':registerform
    }
    return render(request,'network/register.html',context)

def like_unlike(request,post_id):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'],content='GET REQUEST IS NOT ALLOWED')
    
    try:
        post = NewPost.objects.get(pk=post_id)
    except OperationalError:
        return JsonResponse({
                "error": f"Post with id = {post_id} does not exist."
            }, status=404)
    
    if not request.user.is_authenticated:
        messages.error(request,'Please login before liking any posts.')
        return redirect('login',permanent= True)
    
    # following part is for legit user for liking or disliking 
    # an existing post 
    data = json.loads(request.body)
    if data['do'] == 'Like':
        post.likers.add(request.user)
        return JsonResponse({
                "message": "Success",
                "show": "Unlike",
                "likes":post.likers.count()
            }, status=200)
    else:
        post.likers.remove(request.user)
        return JsonResponse({
                    "message": "Success",
                    "show":"Like",
                    "likes":post.likers.count()
                }, status=200)


def profilepage(request,username):
    
    user_profile = User.objects.filter(username = username).first()
    if request.method == 'PUT':
        if user_profile == None:
            return JsonResponse({'error':'No such user exists'},status=400)
        if request.user.is_authenticated:
            data = json.loads(request.body)         
            if data['do'] == 'follow':
                user_profile.followers.add(request.user)
                return JsonResponse({'success':'Followed successfully.'
                ,'show':'Following'
                ,'followers':user_profile.followers.count()},status = 200)
            elif data['do'] == 'unfollow':
                user_profile.followers.remove(request.user)
                return JsonResponse({'success':'Unfollowed successfully.'
                ,'show':'Follow'
                ,'followers':user_profile.followers.count()},status = 200)
        else:
            return redirect('login',permanent= True)

    # GET request section
    if user_profile != None:
        # logger.info(user_profile.followers.get(username='avisek'))
        # logger.info(type(user_profile.followers.get(username='avisek')))
        # logger.info(user_profile.followers.get(username='avisek').email)
        # logger.info(user_profile.followers.filter(username='avisek'))
        
        # getting all the posts of that user making the posts in reverse. 
        posts = NewPost.objects.filter(author__username=username)
        posts = posts.order_by('-created_time','-id')
        x = user_profile.followers.filter(username=request.user.username).first()
        # logger.info(x)
        # logger.info(request.user.username == '')
        if x != None:
            is_follower = True
        else:
            is_follower = False

        if request.user.is_authenticated: 
            liked_posts = request.user.liked_posts.all()
        else:
            liked_posts = []

        # pagination section
        paginator = Paginator(posts,3)
        page_number = request.GET.get('page',1)
        page_obj = paginator.page(page_number)

        context = {
            'user_profile':user_profile,
            'is_follower':is_follower,
            'all_posts':page_obj.object_list,
            'liked_posts':liked_posts,
            'page_obj':page_obj,
            'page_number':page_number
        }
        return render(request,'network/profilepage.html',context)
    else:
        return render(request,'network/profilepage.html',{'user_profile':None})


@login_required
def following_posts(request):
    # get all the users with who i am followed to
    following = request.user.followed_to.all()

    posts = NewPost.objects.all()
    posts = posts.order_by('-created_time','-id')
    all_following_posts = []
    for post in posts:
        if post.author in following:
            all_following_posts.append(post)
    
    # pagination section
    paginator = Paginator(all_following_posts,3)
    page_number = request.GET.get('page',1)
    page_obj = paginator.page(page_number)

    context ={
        'all_posts':page_obj.object_list,
        'liked_posts':request.user.liked_posts.all(),
        'page_obj':page_obj,
        'page_number':page_number
    }

    return render(request,'network/following_posts.html',context)

from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login
from .forms import LoginForm,RegistrationForm,UserProfileForm,UserInfoForm,UserForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import UserInfo,UserProfile,HeadPortrait
from django.urls import resolve
import re,os
from django.conf import settings

# def user_login(request):
#     if request.method == "POST":
#         login_form = LoginForm(request.POST)
#         if login_form.is_valid():
#             cd = login_form.cleaned_data
#             user = authenticate(username = cd['username'],password = cd['password'])
#
#             if user:
#                 login(request, user)
#                 return HttpResponse('登陆成功')
#             else:
#                 return HttpResponse('用户名密码错误')
#         else:
#             return HttpResponse('无效凭证')
#
#     if request.method == "GET":
#         login_form = LoginForm()
#         return render(request, 'account/login.html', {'form':login_form})

def register(request):
    if request.method == 'POST':
        user_form = RegistrationForm(request.POST)
        userprofilefile_form = UserProfileForm(request.POST)
        if user_form.is_valid()*userprofilefile_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            new_profile = userprofilefile_form.save(commit=False)
            new_profile.user = new_user
            new_profile.save()

            UserInfo.objects.create(user = new_user)
            HeadPortrait.objects.create(user = new_user)
            return redirect('/account/register_done/')
        else:
            return HttpResponse('注册失败。')
    else:
        user_form = RegistrationForm()
        userprofilefile_form = UserProfileForm()
        return  render(
            request,'account/register.html',{'form':user_form,'profile':userprofilefile_form}
        )

def register_done(request):
    if request.META.get('HTTP_REFERER'):
        ref_url = request.META.get('HTTP_REFERER')
        if resolve(re.split(request.META.get('HTTP_HOST'), ref_url)[1]).url_name == resolve(
                '/account/register/').url_name:
            text = '注册成功！三秒钟后转入登录，如果长时间没有响应请直接点击：'
            url = 'http://'+request.META.get('HTTP_HOST')+'/account/login/'
        else:
            text = '错误！请从注册页面转入！三秒后跳转至上一页面。'
            url = ref_url

    else:
        text = '错误！请从注册页面转入！三秒后跳转至首页。'
        url = 'http://'+request.META.get('HTTP_HOST')
    return render(
        request, 'account/register_done.html', {'url': url, 'text': text}
    )

@login_required(login_url='/account/login/')
def user_profile(request):
    user = User.objects.get(username = request.user.username)
    userprofile = UserProfile.objects.get(user = user)
    userinfo = UserInfo.objects.get(user = user)
    headportrait = HeadPortrait.objects.get(user = user)
    if not headportrait.avatar:
        img = os.path.join(settings.MEDIA_ROOT,'user_head_portrait/HZ.jpg')
    else:
        img = headportrait.avatar_thumbnail_large.url
    return render(
        request,'account/user_page.html',{'user':user,'userprofile':userprofile,'userinfo':userinfo,'img':img}
    )

@login_required(login_url='/account/login/')
def user_profile_edit(request):
    user = User.objects.get(username = request.user.username)
    userprofile = UserProfile.objects.get(user = user)
    userinfo = UserInfo.objects.get(user = user)
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        userprofile_form = UserProfileForm(request.POST)
        userinfo_form = UserInfoForm(request.POST)
        if user_form.is_valid()*userprofile_form.is_valid()*userinfo_form.is_valid():
            user_cd = user_form.cleaned_data
            userprofile_cd = userprofile_form.cleaned_data
            userinfo_cd = userinfo_form.cleaned_data
            user.email = user_cd['email']

            userprofile.birth = userprofile_cd['birth']
            userprofile.company = userprofile_cd['company']
            userprofile.phone = userprofile_cd['phone']
            userprofile.title = userprofile_cd['title']
            userprofile.weixin = userprofile_cd['weixin']
            userinfo.field = userinfo_cd['field']
            userinfo.style = userinfo_cd['style']
            user.save()
            userprofile.save()
            userinfo.save()
        return redirect('/account/user_page/')
    else:
        user_form = UserForm(instance=request.user)
        userprofile_form = UserProfileForm(initial={
            'birth':userprofile.birth,'phone':userprofile.phone,'company':userprofile.company,'title':userprofile.title,
            'weixin':userprofile.weixin,
        })
        userinfo_form = UserInfoForm(initial={
            'field':userinfo.field,'style':userinfo.style,
        })
        return render(
            request,'account/user_page_edit.html',{
                'user_form':user_form,'userprofile_form':userprofile_form,'userinfo_form':userinfo_form
            }
        )

@login_required(login_url='/account/login')
def upload_image(request):
    user = User.objects.get(username=request.user.username)
    headportrait = HeadPortrait.objects.get(user = user)
    if request.method == 'POST':
        head = request.POST['head']
        headportrait.avatar = head
        headportrait.save()
        return HttpResponse('1')
    else:
        return render(request,'account/user_head_upload.html',)
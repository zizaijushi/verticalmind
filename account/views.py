from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate,login
from .forms import LoginForm,RegistrationForm,UserProfileForm

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
        if user_form.is_valid()*userprofilefile_form():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            new_profile = userprofilefile_form.save(commit=False)
            new_profile.user = new_user
            new_profile.save
            return HttpResponse("注册成功！")
        else:
            return HttpResponse('注册失败。')
    else:
        user_form = RegistrationForm()
        userprofilefile_form = UserProfileForm()
        return  render(
            request,'account/register.html',{'form':user_form,'profile':userprofilefile_form}
        )
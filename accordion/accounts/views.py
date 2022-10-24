from django.shortcuts import render
from django.contrib.auth.models import User
from accounts.models import UserProfile
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def signup(request, *args, **kwargs):
    new_user = None
    if request.method == 'POST':
        fields = ['username', 'email', 'password1', 'password2']
        data = {field: request.POST.get(field) for field in fields}
        new_user = User.objects.create_user(**data)
        new_user.save()
        new_user_profile = UserProfile(user=new_user)
        new_user_profile.save()
        return JsonResponse({'status': 'created'})
    return JsonResponse({'status': 'error'})


    
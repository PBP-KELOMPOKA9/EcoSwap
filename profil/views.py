from django.shortcuts import render

# fungsi untuk nampilin halaman login
def login_view(request):
    return render(request, 'login.html')
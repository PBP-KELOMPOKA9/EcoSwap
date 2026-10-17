from django.shortcuts import render

# fungsi untuk nampilin halaman login
def login_view(request):
    return render(request, 'login.html')

    # fungsi untuk nampilin halaman register
def register_view(request):
    return render(request, 'register.html')
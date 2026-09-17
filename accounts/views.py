from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect


def login_view(request):
    if request.user.is_authenticated:
        return redirect("post_login_redirect")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("post_login_redirect")
        messages.error(request, "Invalid username or password.")
        return render(request, "accounts/login.html")

    return render(request, "accounts/login.html")


@login_required
def post_login_redirect(request):
    """Send the user to the right dashboard based on their group."""
    user = request.user
    if user.is_superuser or user.groups.filter(name="Teacher").exists():
        return redirect("teacher_dashboard")
    if user.groups.filter(name="Student").exists():
        return redirect("student_result")
    messages.error(request, "Your account has no role assigned. Contact admin.")
    logout(request)
    return redirect("login")


def logout_view(request):
    logout(request)
    return redirect("login")

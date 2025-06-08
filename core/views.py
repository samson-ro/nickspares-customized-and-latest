from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse
from .forms import UserRegisterForm
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.views import LogoutView


@login_required
def dashboard(request):
    return render(request, 'core/dashboard.html')

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def get_success_url(self):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return reverse('admin:index')
        return reverse('dashboard')

    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().username}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)
    
class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        list(messages.get_messages(request))
        messages.success(request, "You have been logged out successfully.")
        return super().dispatch(request, *args, **kwargs)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form, 'title': 'Register'})
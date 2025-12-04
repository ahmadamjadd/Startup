import os
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
# New email-related imports
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from .forms import UserRegisterForm, QuizForm, EmailAuthenticationForm
from .models import RoommateProfile, User


def email_user(request, user):
    """Sends a verification email to the user."""
    try:
        current_site = get_current_site(request)
        mail_subject = 'Activate your Roommate Finder account.'
        message = render_to_string('acc_active_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })
        to_email = user.email
        send_mail(
            mail_subject,
            message,
            os.getenv('EMAIL_ADDRESS'),
            [to_email]
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Set the user as active and save
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Thank you for your email confirmation. You are now logged in!')
        return redirect('quiz')
    else:
        messages.error(request, 'Activation link is invalid or expired!')
        return redirect('register')


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.set_password(form.cleaned_data['password'])
            user.save()
            if email_user(request, user):
                messages.info(request, 'Please confirm your email address to complete the registration.')
                return redirect('login')
            else:
                user.delete()
                messages.error(request, 'Registration failed due to an email error. Please try again.')
                return redirect('register')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(data=request.POST)
        if form.is_valid():
            user  = form.get_user()
            login(request, user)
            try:
                if user.roommateprofile:
                    return redirect('dashboard')
            except RoommateProfile.DoesNotExist:
                return redirect('quiz')
    else:
        form = EmailAuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def quiz_view(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('dashboard')
    else:
        form = QuizForm()
    return render(request, 'quiz.html', {'form': form})

@login_required
def dashboard_view(request):
    try:
        my_profile = request.user.roommateprofile
    except RoommateProfile.DoesNotExist:
        return redirect('quiz')

    all_profiles = RoommateProfile.objects.exclude(user=request.user)
    matches = []

    for other in all_profiles:
        score = 100

        if my_profile.sleep_schedule != other.sleep_schedule:
            score -= 25

        if my_profile.study_habit != other.study_habit:
            score -= 15

        clean_diff = abs(my_profile.cleanliness_level - other.cleanliness_level)
        score -= (clean_diff * 5)

        noise_diff = abs(my_profile.noise_tolerance - other.noise_tolerance)
        score -= (noise_diff * 5)

        final_score = max(score, 0)

        matches.append({
            'name': other.user.first_name or other.user.username,
            'score': final_score,
            'room': other.hostel_room_no,
            'sleep': other.sleep_schedule,
            'clean': other.cleanliness_level,
            'profile': other
        })

    matches.sort(key=lambda x: x['score'], reverse=True)
    top_matches = matches[:5]

    return render(request, 'dashboard.html', {'matches': top_matches})

def logout_view(request):
    logout(request)
    return redirect('login')
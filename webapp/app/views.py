import os
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from .models import RoommateProfile, User, MatchInteraction
from .forms import UserRegisterForm, QuizForm, EmailAuthenticationForm, UpdateForm
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Max, Avg


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
                if hasattr(user, 'roommateprofile'):
                    return redirect('dashboard')
                else:
                    return redirect('quiz')
            except RoommateProfile.DoesNotExist:
                return redirect('quiz')
    else:
        form = EmailAuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def quiz_view(request):
    if hasattr(request.user, 'roommateprofile'):
        return redirect('dashboard')

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

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def add_phone_number(request):
    """Separate view to handle existing users adding a phone number"""
    if request.method == 'POST':
        form = UpdateForm(request.POST, instance=request.user.roommateprofile)
        if form.is_valid():
            form.save()
            messages.success(request, "Phone number updated! You are now visible to matches.")
            return redirect('dashboard')
        else:
            messages.error(request, "Please enter a valid phone number starting with 03.")
    return redirect('dashboard')

@login_required
def dashboard_view(request):
    try:
        my_profile = request.user.roommateprofile
    except RoommateProfile.DoesNotExist:
        return redirect('quiz')

    missing_phone = False
    phone_form = None

    if not my_profile.phone_number:
        missing_phone = True
        phone_form = UpdateForm(instance=my_profile)

    all_profiles = RoommateProfile.objects.exclude(user=request.user)
    matches = []

    for other in all_profiles:
        # --- YOUR EXISTING DISTANCE METRIC LOGIC ---
        score = 100
        if my_profile.sleep_schedule != other.sleep_schedule: score -= 25
        if my_profile.study_habit != other.study_habit: score -= 15
        score -= (abs(my_profile.cleanliness_level - other.cleanliness_level) * 5)
        score -= (abs(my_profile.noise_tolerance - other.noise_tolerance) * 5)
        final_score = max(score, 0)
        # -------------------------------------------

        matches.append({
            'name': other.user.first_name or other.user.username,
            'score': final_score,
            'sleep': other.sleep_schedule,
            'clean': other.cleanliness_level,
            'phone': other.phone_number,
            'profile': other,
            'user_id': other.user.id # Needed for the click tracking link
        })

    matches.sort(key=lambda x: x['score'], reverse=True)
    top_matches = matches[:5]

    # --- METRIC LOGGING (Metrics 1 & 3) ---
    # We record that these matches were "Viewed"
    for match in top_matches:
        # update_or_create ensures we track "Unique" views per pair (or updates the timestamp if seen again)
        MatchInteraction.objects.update_or_create(
            viewer=request.user,
            target=match['profile'].user,
            defaults={'match_score': match['score']}
        )
    # --------------------------------------

    context = {
        'matches': top_matches,
        'missing_phone': missing_phone,
        'phone_form': phone_form
    }

    return render(request, 'dashboard.html', context)

@login_required
def track_whatsapp_click(request, target_id):
    """
    Intermediary view to log the click (Metric 1) before redirecting to WhatsApp.
    """
    try:
        target_user = User.objects.get(pk=target_id)
        # Find the interaction record and mark it as clicked
        interaction = MatchInteraction.objects.filter(
            viewer=request.user,
            target=target_user
        ).first()

        if interaction:
            interaction.whatsapp_clicked = True
            interaction.save()

        # Redirect to WhatsApp
        phone_number = target_user.roommateprofile.phone_number
        if phone_number:
            wa_url = f"https://wa.me/{phone_number}?text=Hey!%20I%20saw%20we%20matched%20on%20Roomify."
            return redirect(wa_url)

    except User.DoesNotExist:
        pass

    return redirect('dashboard')

@staff_member_required
def metrics_dashboard(request):
    """
    Calculates the 3 requested metrics for the admin.
    """
    if not request.user.is_staff:
        return redirect('dashboard')

    total_views = MatchInteraction.objects.count()
    total_clicks = MatchInteraction.objects.filter(whatsapp_clicked=True).count()
    mcr = (total_clicks / total_views * 100) if total_views > 0 else 0

    total_users = User.objects.count()
    total_profiles = RoommateProfile.objects.count()
    pcr = (total_profiles / total_users * 100) if total_users > 0 else 0

    avg_top_score_data = MatchInteraction.objects.values('viewer').annotate(max_score=Max('match_score')).aggregate(Avg('max_score'))
    avg_top_score = avg_top_score_data['max_score__avg'] or 0

    context = {
            'mcr': mcr,
            'pcr': pcr,
            'avg_top_score': avg_top_score,
            'total_clicks': total_clicks,
            'total_views': total_views,
            'total_users': total_users,
            'total_profiles': total_profiles,
        }

    return render(request, 'metrics.html', context)
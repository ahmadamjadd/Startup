from django.db import models
from django.contrib.auth.models import User

class RoommateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    SLEEP_CHOICES = [
        ('Early', 'Early Bird (10 PM - 6 AM)'),
        ('Late', 'Night Owl (2 AM - 10 AM)'),
    ]
    sleep_schedule = models.CharField(max_length=10, choices=SLEEP_CHOICES)

    CLEANLINESS_CHOICES = [(i, str(i)) for i in range(1, 6)]
    cleanliness_level = models.IntegerField(choices=CLEANLINESS_CHOICES, help_text="1 (Messy) to 5 (Super Clean)")

    NOISE_CHOICES = [(i, str(i)) for i in range(1, 6)]
    noise_tolerance = models.IntegerField(choices=NOISE_CHOICES, help_text="1 (Need Silence) to 5 (Party Mode)")

    STUDY_CHOICES = [
        ('Morning', 'Morning'),
        ('Night', 'Night'),
        ('Mix', 'Mix'),
    ]
    study_habit = models.CharField(max_length=10, choices=STUDY_CHOICES)

    def __str__(self):
        return f"{self.user.username}'s Profile"
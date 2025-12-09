from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class RoommateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    phone_regex = RegexValidator(
        regex=r'^03\d{9}$',
        message="Phone number must be entered in the format: '03001234567'"
    )

    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=11,
        blank=True,
        null=True
    )

    SLEEP_CHOICES = [('Early', 'Early Bird'), ('Late', 'Night Owl')]
    sleep_schedule = models.CharField(max_length=10, choices=SLEEP_CHOICES)

    CLEANLINESS_CHOICES = [(i, str(i)) for i in range(1, 6)]
    cleanliness_level = models.IntegerField(choices=CLEANLINESS_CHOICES)

    NOISE_CHOICES = [(i, str(i)) for i in range(1, 6)]
    noise_tolerance = models.IntegerField(choices=NOISE_CHOICES)

    STUDY_CHOICES = [('Morning', 'Morning'), ('Night', 'Night'), ('Mix', 'Mix')]
    study_habit = models.CharField(max_length=10, choices=STUDY_CHOICES)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class MatchInteraction(models.Model):
    viewer = models.ForeignKey(User, related_name='viewer_interactions', on_delete=models.CASCADE)
    target = models.ForeignKey(User, related_name='target_interactions', on_delete=models.CASCADE)
    match_score = models.IntegerField()
    timestamp = models.DateTimeField(auto_now=True)
    whatsapp_clicked = models.BooleanField(default=False)

    class Meta:
        pass

    def __str__(self):
        return f"{self.viewer} -> {self.target} ({self.match_score}%)"
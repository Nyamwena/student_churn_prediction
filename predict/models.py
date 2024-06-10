from django.db import models
from django.contrib.auth.models import User

class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    maritalstatus = models.CharField(max_length=10)
    high_school_gpa = models.FloatField()
    entrance_score = models.FloatField()
    studyprogram = models.CharField(max_length=100)
    year_of_study = models.IntegerField()
    modeofstudy = models.CharField(max_length=20)
    parttimefulltime = models.CharField(max_length=20)
    scholarship = models.BooleanField()
    financial_aid = models.BooleanField()
    tuitionstatus = models.CharField(max_length=20)
    university_gpa = models.FloatField()
    course_failures = models.IntegerField()
    academic_probation = models.BooleanField()
    library_uses = models.IntegerField()
    distance_from_home = models.FloatField()
    employmentstatus = models.CharField(max_length=20)
    churn = models.BooleanField()

    def __str__(self):
        return f"{self.user.username} - {self.studyprogram} - {'Churn' if self.churn else 'No Churn'}"

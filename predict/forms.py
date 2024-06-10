from django import forms

class ChurnPredictionForm(forms.Form):
    age = forms.IntegerField(label='Age')
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female'), ('Other', 'Other')], label='Gender')
    maritalstatus = forms.ChoiceField(choices=[('Single', 'Single'), ('Married', 'Married'), ('Divorced', 'Divorced')], label='Marital Status')
    high_school_gpa = forms.FloatField(label='High School GPA')
    entrance_score = forms.FloatField(label='Entrance Score')
    studyprogram = forms.ChoiceField(choices=[
        ("Geography and Environmental Science", "Geography and Environmental Science"),
        ("Statistics and Operations Research", "Statistics and Operations Research"),
        ("Computer Sciences", "Computer Sciences"),
        # Add all other programs here
    ], label='Study Program')
    year_of_study = forms.IntegerField(label='Year of Study')
    modeofstudy = forms.ChoiceField(choices=[('Block', 'Block'), ('Distance', 'Distance')], label='Mode of Study')
    parttimefulltime = forms.ChoiceField(choices=[('Full-time', 'Full-time'), ('Part-time', 'Part-time')], label='Part-Time/Full-Time')
    scholarship = forms.BooleanField(required=False, label='Scholarship')
    financial_aid = forms.BooleanField(required=False, label='Financial Aid')
    tuitionstatus = forms.ChoiceField(choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid'), ('Exempt', 'Exempt')], label='Tuition Status')
    university_gpa = forms.FloatField(label='University GPA')
    course_failures = forms.IntegerField(label='Course Failures')
    academic_probation = forms.BooleanField(required=False, label='Academic Probation')
    library_uses = forms.IntegerField(label='Library Uses')
    distance_from_home = forms.FloatField(label='Distance From Home')
    employmentstatus = forms.ChoiceField(choices=[('Employed', 'Employed'), ('Unemployed', 'Unemployed'), ('Student', 'Student')], label='Employment Status')

from django.shortcuts import render, redirect
from .forms import ChurnPredictionForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views, logout
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io
import urllib, base64

# Load the model, scaler, and label encoders
from .models import Prediction

model_path = 'student_churn_model.pkl'
scaler_path = 'scaler.pkl'
label_encoders_path = 'label_encoders.pkl'

with open(model_path, 'rb') as f:
    model = pickle.load(f)

with open(scaler_path, 'rb') as f:
    scaler = pickle.load(f)

with open(label_encoders_path, 'rb') as f:
    label_encoders = pickle.load(f)


@login_required()
def home(request):
    return render(request, 'predict/home.html')

@login_required()
def predict_churn(request):
    if request.method == 'POST':
        form = ChurnPredictionForm(request.POST)
        if form.is_valid():
            # Extract data from form
            form_data = form.cleaned_data
            data = np.array([
                form_data['age'],
                form_data['gender'],
                form_data['maritalstatus'],
                form_data['high_school_gpa'],
                form_data['entrance_score'],
                form_data['studyprogram'],
                form_data['year_of_study'],
                form_data['modeofstudy'],
                form_data['parttimefulltime'],
                int(form_data['scholarship']),
                int(form_data['financial_aid']),
                form_data['tuitionstatus'],
                form_data['university_gpa'],
                form_data['course_failures'],
                int(form_data['academic_probation']),
                form_data['library_uses'],
                form_data['distance_from_home'],
                form_data['employmentstatus'],
            ]).reshape(1, -1)

            print("Data before encoding:", data)
            print("Form data keys:", form_data.keys())
            print("Label encoder keys:", label_encoders.keys())

            # Encode categorical data
            categorical_columns = ['gender', 'maritalstatus', 'studyprogram', 'modeofstudy', 'parttimefulltime', 'tuitionstatus', 'employmentstatus']
            for col in categorical_columns:
                print(f"Encoding column: {col}")
                le = label_encoders.get(col)
                if le:
                    idx = list(form_data.keys()).index(col)
                    data[0, idx] = le.transform([str(data[0, idx])])[0]
                else:
                    print(f"Label encoder for {col} not found")

            print("Data after encoding:", data)

            # Convert boolean fields to integers (already done during data array creation)

            # Ensure all features are correctly handled
            numerical_indices = [i for i, col in enumerate(form_data.keys()) if col not in categorical_columns]
            print("Numerical indices:", numerical_indices)
            print("Data before scaling:", data)

            # Create a full data array including all features
            full_data = np.zeros((1, 18))  # Replace 18 with the total number of features used during training
            for i, idx in enumerate(numerical_indices):
                full_data[0, i] = data[0, idx]

            for i, col in enumerate(categorical_columns, start=len(numerical_indices)):
                full_data[0, i] = data[0, list(form_data.keys()).index(col)]

            print("Full data before scaling:", full_data)

            # Scale the numerical data
            full_data = scaler.transform(full_data)

            print("Full data after scaling:", full_data)

            # Predict churn
            prediction = model.predict(full_data)
            prediction_text = 'Yes' if prediction[0] else 'No'

            # Save the prediction
            Prediction.objects.create(
                user=request.user,
                age=form_data['age'],
                gender=form_data['gender'],
                maritalstatus=form_data['maritalstatus'],
                high_school_gpa=form_data['high_school_gpa'],
                entrance_score=form_data['entrance_score'],
                studyprogram=form_data['studyprogram'],
                year_of_study=form_data['year_of_study'],
                modeofstudy=form_data['modeofstudy'],
                parttimefulltime=form_data['parttimefulltime'],
                scholarship=form_data['scholarship'],
                financial_aid=form_data['financial_aid'],
                tuitionstatus=form_data['tuitionstatus'],
                university_gpa=form_data['university_gpa'],
                course_failures=form_data['course_failures'],
                academic_probation=form_data['academic_probation'],
                library_uses=form_data['library_uses'],
                distance_from_home=form_data['distance_from_home'],
                employmentstatus=form_data['employmentstatus'],
                churn=bool(prediction[0])
            )

            return render(request, 'predict/result.html', {'prediction': prediction_text})
    else:
        form = ChurnPredictionForm()

    return render(request, 'predict/form.html', {'form': form})

class LoginView(auth_views.LoginView):
    template_name = 'predict/login.html'

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def generate_report(request):
    # Query the database for predictions
    predictions = Prediction.objects.all()

    # Convert to DataFrame
    df = pd.DataFrame.from_records(predictions.values())

    # Prepare plots
    plots = []

    # Function to save plot to string
    def save_plot_to_string(fig):
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = urllib.parse.quote(string)
        return uri

    # Churn by study program
    churn_by_studyprogram = df.groupby('studyprogram')['churn'].value_counts().unstack().fillna(0)
    fig, ax = plt.subplots(figsize=(10, 6))
    churn_by_studyprogram.plot(kind='bar', stacked=True, ax=ax)
    ax.set_title('Churn by Study Program (Bar)')
    ax.set_xlabel('Study Program')
    ax.set_ylabel('Number of Students')
    plt.xticks(rotation=45)
    plots.append(save_plot_to_string(fig))

    fig, ax = plt.subplots(figsize=(10, 6))
    churn_by_studyprogram.plot(kind='pie', subplots=True, ax=ax, autopct='%1.1f%%')
    ax.set_title('Churn by Study Program (Pie)')
    ax.set_ylabel('')
    plots.append(save_plot_to_string(fig))

    # Churn by gender
    churn_by_gender = df.groupby('gender')['churn'].value_counts().unstack().fillna(0)
    fig, ax = plt.subplots(figsize=(10, 6))
    churn_by_gender.plot(kind='bar', stacked=True, ax=ax)
    ax.set_title('Churn by Gender (Bar)')
    ax.set_xlabel('Gender')
    ax.set_ylabel('Number of Students')
    plt.xticks(rotation=0)
    plots.append(save_plot_to_string(fig))

    fig, ax = plt.subplots(figsize=(10, 6))
    churn_by_gender.plot(kind='pie', subplots=True, ax=ax, autopct='%1.1f%%')
    ax.set_title('Churn by Gender (Pie)')
    ax.set_ylabel('')
    plots.append(save_plot_to_string(fig))

    # Churn by marital status
    churn_by_maritalstatus = df.groupby('maritalstatus')['churn'].value_counts().unstack().fillna(0)
    fig, ax = plt.subplots(figsize=(10, 6))
    churn_by_maritalstatus.plot(kind='bar', stacked=True, ax=ax)
    ax.set_title('Churn by Marital Status (Bar)')
    ax.set_xlabel('Marital Status')
    ax.set_ylabel('Number of Students')
    plt.xticks(rotation=0)
    plots.append(save_plot_to_string(fig))

    fig, ax = plt.subplots(figsize=(10, 6))
    churn_by_maritalstatus.plot(kind='pie', subplots=True, ax=ax, autopct='%1.1f%%')
    ax.set_title('Churn by Marital Status (Pie)')
    ax.set_ylabel('')
    plots.append(save_plot_to_string(fig))

    # Churn by year of study
    churn_by_yearofstudy = df.groupby('year_of_study')['churn'].value_counts().unstack().fillna(0)
    fig, ax = plt.subplots(figsize=(10, 6))
    churn_by_yearofstudy.plot(kind='bar', stacked=True, ax=ax)
    ax.set_title('Churn by Year of Study (Bar)')
    ax.set_xlabel('Year of Study')
    ax.set_ylabel('Number of Students')
    plt.xticks(rotation=0)
    plots.append(save_plot_to_string(fig))

    fig, ax = plt.subplots(figsize=(10, 6))
    churn_by_yearofstudy.plot(kind='pie', subplots=True, ax=ax, autopct='%1.1f%%')
    ax.set_title('Churn by Year of Study (Pie)')
    ax.set_ylabel('')
    plots.append(save_plot_to_string(fig))

    return render(request, 'predict/report.html', {'plots': plots})

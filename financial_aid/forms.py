from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Student, FinancialAidApplication

class StudentRegistrationForm(UserCreationForm):
    student_id = forms.CharField(max_length=20)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    phone_number = forms.CharField(max_length=15)
    age = forms.IntegerField()
    school = forms.CharField(max_length=100)
    location = forms.CharField(max_length=100)
    economic_status = forms.ChoiceField(choices=Student.ECONOMIC_STATUS)
    disability_status = forms.ChoiceField(choices=Student.DISABILITY_STATUS)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'student_id', 
                 'date_of_birth', 'phone_number', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'student'
        if commit:
            user.save()
            Student.objects.create(
                user=user,
                student_id=self.cleaned_data['student_id'],
                date_of_birth=self.cleaned_data['date_of_birth'],
                phone_number=self.cleaned_data['phone_number']
            )
        return user

class ManagerRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'manager'
        if commit:
            user.save()
        return user

class FinancialAidApplicationForm(forms.ModelForm):
    class Meta:
        model = FinancialAidApplication
        fields = ['academic_year', 'requested_amount', 'purpose', 'supporting_documents'] 
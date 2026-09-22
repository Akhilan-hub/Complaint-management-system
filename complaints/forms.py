from django import forms
from django.contrib.auth.models import User
from .models import Complaint

class UserRegisterForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Full Name (e.g., Arun Kumar)',
            'autocomplete': 'off'
        }),
        label="Full Name"
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email Address',
            'autocomplete': 'off'
        }),
        label="Email"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password',
            'autocomplete': 'new-password'
        }),
        required=True,
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm Password',
            'autocomplete': 'new-password'
        }),
        required=True,
        label="Confirm Password"
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
            raise forms.ValidationError("A user with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

class UserLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your email or username',
            'autocomplete': 'off'
        }),
        label="Email / Username"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password',
            'autocomplete': 'off'
        }),
        label="Password"
    )

class ComplaintSubmissionForm(forms.ModelForm):
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Brief title summarizing the issue'
        })
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'rows': 4,
            'placeholder': 'Detailed description of the complaint...'
        })
    )
    image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'form-file-input',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = Complaint
        fields = ['title', 'description', 'image']

class ResolutionSubmissionForm(forms.Form):
    resolution_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'rows': 4,
            'placeholder': 'Provide detailed resolution steps taken...'
        }),
        required=True,
        label="Resolution Description"
    )
    resolution_image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'form-file-input',
            'accept': 'image/*'
        }),
        required=True,
        label="Resolution Evidence Image"
    )

class ManualConfirmForm(forms.Form):
    admin_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your Admin Password',
            'autocomplete': 'new-password'
        }),
        required=True,
        label="Admin Password Authentication"
    )

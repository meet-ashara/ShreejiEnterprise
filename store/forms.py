from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Contact

# Get the custom user model
User = get_user_model()

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Your Email'}),
            'subject': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Message'}),
        }


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label="Email", widget=forms.EmailInput(attrs={"autocomplete": "email"}))

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    is_active = forms.BooleanField(initial=True, required=False)  # This is optional, can be removed if not needed

    class Meta:
        model = User
        fields = ["email", "password1", "password2"]  # No "username" field, use "email" instead

    def save(self, commit=True):
        user = super().save(commit=False)

        # Save email as username (if using email as the username)
        user.email = self.cleaned_data["email"]
        
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "input-field", "placeholder": field.label})


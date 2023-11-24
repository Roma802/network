from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import ClearableFileInput

from network.models import Post, Comment, User, UserProfile


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'file']
        # widgets = {
        #     'file': forms.FileInput(attrs={'accept':'image/*,video/*'}),
        # }

    text = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'text-field-style'})
    )

    file = forms.FileField(
        # help_text="",
        # label="",
        initial="Your name",
        widget=forms.FileInput(attrs={'accept':'image/*,video/*', 'class': 'file-input-style'})
    )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(
                attrs={'placeholder': 'Enter your comment here...', 'rows': 4,
                       'cols': 40}),
        }


class CustomUserCreationForm(UserCreationForm):
    # photo = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'type': 'text',
            'name': 'username',
            'placeholder': 'Username'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'type': 'email',
            'name': 'email',
            'placeholder': 'Email Address'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'type': 'password',
            'name': 'password',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'type': 'password',
            'name': 'confirmation',
            'placeholder': 'Confirmation your password'
        })

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_image', 'bio', 'birth_date']

    profile_image = forms.FileField(
        widget=forms.FileInput(attrs={'accept':'image/*', 'class': 'file-input-style'}),
        required = False
    )

    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'text-field-style'}),
        required = False
    )

    birth_date = forms.DateField(
        widget=forms.DateInput(format=('%Y-%m-%d'),
        attrs={'class': 'form-control',
               'type': 'date'
              }),
        required = False
    )


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'text',
                                      'name': 'username', 'placeholder': 'Username'})
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'type': 'email',
                                       'name': 'email', 'placeholder': 'Email Address'})
    )


class SearchForm(forms.Form):
    query = forms.CharField(label='', max_length=100,
                            widget=forms.TextInput(attrs={'placeholder': 'Search...'}))





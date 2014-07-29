from django import forms
from django.contrib.auth.models import User
from rango.models import Page, Category, UserProfile


# each Form inherits from ModelForm, a helper class

class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text="Please enter the category name.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    # inline class to provide additional information on the form
    class Meta:
        # provide an association between the ModelForm and a model
        model = Category


class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128, help_text="Please enter the title of the page.")
    url = forms.URLField(max_length=200, help_text="Please enter the URL of the page.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        # provide an association between the ModelForm and a model
        model = Page

        # what fields do we want to include in our form?
        fields = ('title', 'url', 'views')

    def clean(self):
        '''
        in scenarios where user input may not be entirely correct, we can ovveride
        the clean() method implemented in ModelForm. this method is called upon
        before saving form data to a new model instance.
        '''
        
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        # if url is not empty and doesn't start with 'http://', prepend
        # note: startswith is pretty cool
        if url and not url.startswith('http://'):
            url = 'http://' + url            
            cleaned_data['url'] = url

        return cleaned_data


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        '''
        each Meta class describes additional properties about the particular ModelForm
        class it belongs to. It must at a bare minimum supply a model field
        '''
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')

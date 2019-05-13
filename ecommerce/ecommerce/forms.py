from django import forms

class ContactForm(forms.Form):
    fullname = forms.CharField(widget = forms.TextInput(attrs = {
        'class': 'form-control',
        'placeholder': 'Your full name'
    }))
    email = forms.EmailField(widget = forms.EmailInput(attrs = {
        'class': 'form-control',
        'placeholder': 'Your email'
    }))
    content = forms.CharField(widget = forms.Textarea(attrs = {
        'class': 'form-control',
        'placeholder': 'Your message'
    }))
    feedback = forms.CharField(label = "Leave a feedback, it's helpful", widget = forms.Textarea(attrs = {
        'class': 'form-control',
        'placeholder': 'Your feedback'
    }))

    def clean_fullname(self):
        fullname = self.cleaned_data.get('fullname')
        if len(fullname) < 3:
            raise forms.ValidationError("Fullname should be at least 3 characters long")
        return fullname

    def clean_email(self):
        email = self.cleaned_data['email']
        if 'test.com' in email or 'abc.com' in email:
            raise forms.ValidationError("Invalid email used")
        return email

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) == 1:
            raise forms.ValidationError("Content must be greater than a character")
        return content

    def clean_feedback(self):
        feedback = self.cleaned_data.get('feedback')
        if len(feedback) == 1:
            raise forms.ValidationError("Feedback must be greater than a character")
        return feedback
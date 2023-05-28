from django import forms
from .models import Account , UserProfile

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget= forms.PasswordInput(attrs={
        'placeholder':'password'
    }))
    confirm_password = forms.CharField(widget= forms.PasswordInput(attrs={
        'placeholder':'Confirm password'
    }))
    phone_number = forms.CharField(required=False)
    class Meta:
        model = Account
        fields = ['first_name' , 'last_name' , 'phone_number' , 'email' , 'password']
    def __init__(self , *args , **kwargs):
        super(RegistrationForm , self).__init__(*args ,**kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = "First Name"
        # self.fields['phone_number'].widget.attrs['required'] = False
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super(RegistrationForm , self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        
class UserEditForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['first_name' , 'last_name' , 'phone_number']
    def __init__(self , *args , **kwargs):
        super(UserEditForm , self).__init__(*args ,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class UserDetailForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False , error_messages={"invalid":("image files only")} , widget = forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ['address_line1' , "address_line2" , 'city' , 'state' , 'profile_picture' , 'country']
    def __init__(self , *args , **kwargs):
        super(UserDetailForm , self).__init__(*args ,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
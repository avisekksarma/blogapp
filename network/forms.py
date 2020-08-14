from django.contrib.auth.forms import UserCreationForm
from .models import User

# this is a model form to make new users extending the usercreation form.
class UserRegisterform(UserCreationForm):
    class Meta:
        model = User
        fields = ('username','email','password1','password2','image')

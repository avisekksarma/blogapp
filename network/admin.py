from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm,UserChangeForm
from .models import User,NewPost

# get a way to log the errors:
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
filehandler = logging.FileHandler('adminformlog.txt')
filehandler.setFormatter(formatter)
logger.addHandler(filehandler)
# convert the errors to text
from django.utils.encoding import force_text

class Myuserchangeform(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('image','followers')

class Myusercreationform(UserCreationForm):
    def is_valid(self):
        logger.info(force_text(self.errors))
        return super(Myusercreationform, self).is_valid()

    # image = forms.ImageField(upload_to='images/',default='default_user.jpg')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('image','followers')

class UserAdmin(BaseUserAdmin):
    form = Myuserchangeform
    add_form = Myusercreationform
    fieldsets= BaseUserAdmin.fieldsets + ((
        ('Extra information:',{
            'fields':('image','followers')
        }
        )
    ),)

    # add_fieldsets = fieldsets   => i dont know why this makes error because of which i cannot upload image in first go.


admin.site.register(User,UserAdmin)
admin.site.register(NewPost)
from django.contrib import admin
from .models import UserModel,TokenModel,UserCred

# Register your models here.
# admin.site.register(UserModel)
# admin.site.register(TokenModel)
# admin.site.register(UserCred)


#update how the admin panel looks
admin.site.site_header = "AKGconnect"


#update how models are displayed in the admin panel
class UserModelAdmin(admin.ModelAdmin):
    list_display = ('user_id','login_name','first_name','last_name','admission_number','roll_number','email','admission_date','dob','profile_picture_id','aadhaar_number','sms_mobile_number')
    search_fields = ('user_id','login_name','first_name','last_name','admission_number','roll_number','email','admission_date','dob','profile_picture_id','aadhaar_number','sms_mobile_number')
    list_filter = ('user_id','login_name','first_name','last_name','admission_number','roll_number','email','admission_date','dob','profile_picture_id','aadhaar_number','sms_mobile_number')

class TokenModelAdmin(admin.ModelAdmin):
    list_display=('user_id','rx','issued','expires')
    search_fields=('user_id','rx','issued','expires')
    list_filter=('user_id','rx','issued','expires')

class UserCredAdmin(admin.ModelAdmin):
    list_display=('fullname','username','password')
    search_fields=('fullname','username','password')
    list_filter=('fullname','username','password')
    
admin.site.register(UserModel,UserModelAdmin)
admin.site.register(TokenModel,TokenModelAdmin)
admin.site.register(UserCred,UserCredAdmin)            
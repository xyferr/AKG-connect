from django.db import models

class TokenModel(models.Model):
    access_token = models.CharField(max_length=1000)
    token_type = models.CharField(max_length=50)
    expires_in = models.IntegerField()
    context_id = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255)
    logo_id = models.CharField(max_length=255)
    rx = models.CharField(max_length=255)
    change_setting = models.CharField(max_length=255)
    change_status = models.CharField(max_length=255)
    issued = models.CharField(max_length=255)
    expires = models.CharField(max_length=255)
    x_token = models.CharField(max_length=1000,null=True,blank=True)

    def __str__(self):
        return self.user_id

class UserModel(models.Model):
    user_id = models.IntegerField()
    batch_id = models.IntegerField()
    login_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    admission_number = models.CharField(max_length=255)
    roll_number = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    admission_date = models.DateField()
    dob = models.DateField()
    profile_picture_id = models.IntegerField()
    aadhaar_number = models.CharField(max_length=12)
    sms_mobile_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=10)

    def __str__(self):
        return self.login_name
    

class UserCred(models.Model):
    fullname = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.fullname

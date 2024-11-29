import requests
from django.db import migrations , models

TOKEN_ENDPOINT = "https://akgecerp.edumarshal.com/Token"
def set_x_token(apps, schema_editor):
    #use credentials from usercred table and get X_token for each user
    UserCred = apps.get_model('Authentication', 'UserCred')
    TokenModel = apps.get_model('Authentication', 'TokenModel')
    for user in UserCred.objects.all():
        try:
            response = requests.post(
                TOKEN_ENDPOINT,
                data={
                    'grant_type': 'password',
                    'username': user.username,
                    'password': user.password,
                    'remember': 'true',
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

            if response.status_code == 200:
                token_data = response.json()
                # Save the token data to the database
                if TokenModel.objects.filter(user_id=token_data.get('X-UserId')).exists():
                    TokenModel.objects.filter(user_id=token_data.get('X-UserId')).update(
                        x_token = token_data.get('X_Token')
                    )
                else:
                    TokenModel.objects.create(
                        x_token = token_data.get('X_Token')
                    )
            else:
                print('Failed! Please check your credentials again.')
        except Exception as e:
            print(str(e))

class Migration(migrations.Migration):

    dependencies = [
        ('Authentication', '0003_alter_tokenmodel_access_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='tokenmodel',
            name='x_token',
            field=models.CharField(max_length=1000, null=True, blank=True),
        ),
        migrations.RunPython(set_x_token),
    ]

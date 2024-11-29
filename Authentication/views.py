from django.shortcuts import render, redirect
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import UserModel, TokenModel, UserCred
from django.contrib import messages
from datetime import datetime

# Endpoints
TOKEN_ENDPOINT = "https://akgecerp.edumarshal.com/Token"
USER_DETAILS_ENDPOINT = "https://akgecerp.edumarshal.com/api/User/GetByUserId"
ATTENDANCE_ENDPOINT = "https://akgecerp.edumarshal.com/api/SubjectAttendance/GetPresentAbsentStudent"

values = {}

@csrf_exempt
def login_view(request):
    if request.method == "GET":
        return render(request, 'authentication/login.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        values['username'] = username
        values['password'] = password

        try:
            response = requests.post(
                TOKEN_ENDPOINT,
                data={
                    'grant_type': 'password',
                    'username': username,
                    'password': password,
                    'remember': 'true',
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

            if response.status_code == 200:
                token_data = response.json()
                # Save the token data to the database
                if TokenModel.objects.filter(user_id=token_data.get('X-UserId')).exists():
                    TokenModel.objects.filter(user_id=token_data.get('X-UserId')).update(
                        access_token=token_data.get('access_token'),
                        token_type=token_data.get('token_type'),
                        expires_in=token_data.get('expires_in'),
                        context_id=token_data.get('X-ContextId'),
                        user_id=token_data.get('X-UserId'),
                        logo_id=token_data.get('X-LogoId'),
                        rx=token_data.get('X-RX'),
                        change_setting=token_data.get('PChangeSetting'),
                        change_status=token_data.get('PChangeStatus'),
                        issued=token_data.get('.issued'),
                        expires=token_data.get('.expires'),
                        x_token = token_data.get('X_Token')
                    )
                else:
                    TokenModel.objects.create(
                        access_token=token_data.get('access_token'),
                        token_type=token_data.get('token_type'),
                        expires_in=token_data.get('expires_in'),
                        context_id=token_data.get('X-ContextId'),
                        user_id=token_data.get('X-UserId'),
                        logo_id=token_data.get('X-LogoId'),
                        rx=token_data.get('X-RX'),
                        change_setting=token_data.get('PChangeSetting'),
                        change_status=token_data.get('PChangeStatus'),
                        issued=token_data.get('.issued'),
                        expires=token_data.get('.expires'),
                        x_token = token_data.get('X_Token')
                        
                    )
                # Store the user ID in the session
                request.session['user_id'] = token_data.get('X-UserId')
                request.session['access_token'] = token_data.get('access_token')
                request.session['X-ContextId'] = token_data.get('X-ContextId')
                request.session['X-RX'] = token_data.get('X-RX')
                request.session['X_token'] = token_data.get('X_Token')
                
                fetch_user_details(request, token_data.get('X-UserId'), token_data.get('access_token'))
                return redirect('attendance')
            else:
                messages.error(request, 'Failed! Please check your credentials again.')
                return render(request, 'authentication/login.html', {'fieldValues': request.POST})
        except Exception as e:
            messages.error(request, str(e))
            return render(request, 'authentication/login.html', {'fieldValues': request.POST})
    
    return render(request, 'authentication/login.html')

@csrf_exempt
def fetch_user_details(request, user_id, auth_token):
    try:
        response = requests.get(
            f"{USER_DETAILS_ENDPOINT}/{user_id}?y=0",
            headers={'Authorization': f'Bearer {auth_token}'}
        )

        if response.status_code == 200:
            user_data = response.json()
            
            # Parse date fields, handling the time component
            admission_date = datetime.strptime(user_data.get('admissionDate'), '%Y-%m-%dT%H:%M:%S').date()
            dob = datetime.strptime(user_data.get('dob'), '%Y-%m-%dT%H:%M:%S').date()
            values['full_name'] = user_data.get('firstName') + ' ' + user_data.get('lastName')
            create_usercred(values)
            # Save the user data to the database
            if UserModel.objects.filter(user_id=user_data.get('userId')).exists():
                UserModel.objects.filter(user_id=user_data.get('userId')).update(
                    batch_id=user_data.get('batchId'),
                    login_name=user_data.get('loginName'),
                    first_name=user_data.get('firstName'),
                    last_name=user_data.get('lastName'),
                    admission_number=user_data.get('admissionNumber'),
                    roll_number=user_data.get('rollNumber'),
                    email=user_data.get('email'),
                    admission_date=admission_date,
                    dob=dob,
                    profile_picture_id=user_data.get('profilePictureId'),
                    aadhaar_number=user_data.get('aadhaarNumber'),
                    sms_mobile_number=user_data.get('smsMobileNumber'),
                    gender=user_data.get('gender')
                )
                admission_number = user_data.get('admissionNumber')
                request.session['admission_number'] = admission_number
            else:
                UserModel.objects.create(
                    user_id=user_data.get('userId'),
                    batch_id=user_data.get('batchId'),
                    login_name=user_data.get('loginName'),
                    first_name=user_data.get('firstName'),
                    last_name=user_data.get('lastName'),
                    admission_number=user_data.get('admissionNumber'),
                    roll_number=user_data.get('rollNumber'),
                    email=user_data.get('email'),
                    admission_date=admission_date,
                    dob=dob,
                    profile_picture_id=user_data.get('profilePictureId'),
                    aadhaar_number=user_data.get('aadhaarNumber'),
                    sms_mobile_number=user_data.get('smsMobileNumber'),
                    gender=user_data.get('gender')
                )
                admission_number = user_data.get('admissionNumber')
                request.session['admission_number'] = admission_number
            
            return redirect('attendance')
        else:
            messages.error(request, 'Failed to fetch details')
            # return redirect('login')
    except Exception as e:
        messages.error(request, str(e))
        print("Exception occurred:", e)
        # return redirect('login')


def create_usercred(values):
    if UserCred.objects.filter(username=values['username']).exists():
        UserCred.objects.filter(username=values['username']).update(
            fullname=values['full_name'],
            password=values['password']
        )
    else:
        
        UserCred.objects.create(
            fullname=values['full_name'],
            username=values['username'],
            password=values['password']
        )


#Since i have added one more field to my token model that is X_token , i will contruct a function that input username and passwords from usercred model and update the token model of every user so that X_token field is fetched again
def fetch_xtoken():
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
    print("X_Token fetched successfully")
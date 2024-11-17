from django.shortcuts import render
import requests
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from models import UserModel, TokenModel, UserCred
#import models from authentication
from Authentication.models import TokenModel, UserModel, UserCred
from django.contrib import messages
from django.views.decorators.clickjacking import xframe_options_exempt


Attendance_endpoint = "https://akgecerp.edumarshal.com/api/SubjectAttendance/GetPresentAbsentStudent"

# Create your views here.

# @xframe_options_exempt
def Get_attendance(request):
    values={}
    try:
        #we will send a get request to attendance_endpoint , in this first we will fetch the userid from the session and then the auth token from the databse using that userid
        user_id = request.session.get('user_id')
        token = TokenModel.objects.get(user_id=user_id)
        contextid = token.context_id
        access_token = token.access_token
        rx = token.rx
        attendance_url = f"{Attendance_endpoint}?isDateWise=false&termId=0&userId={user_id}&y=0"

        #we will send the get request to the attendance endpoint
        response = requests.get(
            attendance_url,
            headers={
                'Authorization': f'Bearer {access_token}',
                'X-UserId': user_id,
                'X-ContextId': contextid,
                'X-RX': rx
            }
        )
        if response.status_code != 200:
            messages.error(request, 'Failed to fetch attendance data')
            print("Failed to fetch attendance data")
            return HttpResponseBadRequest
        #we will get the response in json format
        attendance_data = response.json()
        stdSubAtdDetails = attendance_data.get("stdSubAtdDetails", {})
        overallAbsent = stdSubAtdDetails.get("overallLecture") - stdSubAtdDetails.get("overallPresent")
        values = {
            "overallPresent": stdSubAtdDetails.get("overallPresent"),
            "overallLecture": stdSubAtdDetails.get("overallLecture"),
            "overallPercentage": stdSubAtdDetails.get("overallPercentage"),
            "overallAbsent": overallAbsent,
        }
        print(values)
        context={
            'values':values
        }
        return render(request, 'attendance/index.html', context=context)
        
        
        
    except Exception as e:
        messages.error(request, str(e))
        print("data not fetched" , e)
        values = {
            "overallPresent": 0,
            "overallLecture": 0,
            "overallPercentage": 0
        }
        context={
            'values':values
        }
        # return HttpResponseBadRequest
        return render(request, 'attendance/index.html' , context=context)
    # return render(request, 'attendance/index.html')
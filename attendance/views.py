from django.shortcuts import render
import requests
from django.http import HttpResponseBadRequest
from django.contrib import messages
from datetime import datetime


Attendance_endpoint = "https://akgecerp.edumarshal.com/api/SubjectAttendance/GetPresentAbsentStudent"

# Create your views here.

# @xframe_options_exempt
def Get_attendance(request):
    values={}
    try:
        if not request.session.get('user_id'):
            messages.error(request, 'You are not logged in Clear your cookies/cache and login again')
            return render(request, 'authentication/login.html')
        #we will send a get request to attendance_endpoint , in this first we will fetch the userid from the session and then the auth token from the databse using that userid
        user_id = request.session.get('user_id')
        # token = TokenModel.objects.get(user_id=user_id)
        access_token = request.session.get('access_token')
        
        # contextid = token.context_id
        contextid = request.session.get('X-ContextId')
        
        # access_token = token.access_token
        # rx = token.rx
        rx = request.session.get('X-RX')
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
            "overallPresent": int(stdSubAtdDetails.get("overallPresent")),
            "overallLecture": int(stdSubAtdDetails.get("overallLecture")),
            "overallPercentage": stdSubAtdDetails.get("overallPercentage"),
            "overallAbsent": int(overallAbsent),
        }
        subjects = stdSubAtdDetails.get("subjects", [])
        subIndex={
            
        }
        for i in range(len(subjects)):
            subIndex[subjects[i]["id"]]=i
        
        attendanceData = attendance_data.get("attendanceData", [])
        computed_range = range(len(attendance_data) // len(subjects))
        stdAtdlist = []
        for i in range(0,len(attendanceData),len(subjects)):
            curdict = {}
            rawdate = attendanceData[i]["absentDate"]
            parsed_date = datetime.strptime(rawdate, "%Y-%m-%dT%H:%M:%S")
            formatted_date = parsed_date.strftime("%d-%m-%y")
            curdict['date']=formatted_date
            cur=[]
            
            for j in range(i,i+len(subjects)):
                
                lbl = attendanceData[j]["attendanceLable"]
                
                
                if lbl=="P":
                    cur.append([("P","present")])
                elif lbl=="A":
                    cur.append([("A","absent")])
                elif lbl=="AC":
                    cur.append([("AC","present")])
                else:
                    cur.append([("--",None)])
                    
                
                if j==len(attendanceData):
                    break
            # cur.append({
            #             "value":labelval,
            #             "color":colorval
            #         })
            curdict["values"]  = cur
            stdAtdlist.append(curdict)
        stdAtdlist.sort(key=lambda x: datetime.strptime(x["date"], "%d-%m-%y"))

        extraLectures = attendance_data.get("extraLectures", [])
        for i in range(len(extraLectures)):
            rawdate = extraLectures[i]["absentDate"]
            parsed_date = datetime.strptime(rawdate, "%Y-%m-%dT%H:%M:%S")
            formatted_date = parsed_date.strftime("%d-%m-%y")
            #here binary search to find the formatted_date in stdAtdlist
            low = 0
            high = len(stdAtdlist)-1
            res = -1
            while low<=high:
                mid = (low+high)//2
                d1 = dateHash(stdAtdlist[mid]["date"])
                d2 = dateHash(formatted_date)
                if d1==d2:
                    res = mid
                    break
                elif d1<d2:
                    low = mid+1
                else:
                    high = mid-1
            if stdAtdlist[res]["date"]==formatted_date:
                # print("found" , formatted_date)
                
                ind = subIndex[extraLectures[i]["subjectId"]]
                curval = stdAtdlist[res]["values"][ind]
                lbl = extraLectures[i]["attendanceLable"]

                # Append the string lbl to whatever the current string is
                  # Update the first element
                if lbl == "P":
                    curval.append(("P","present"))
                elif lbl == "A":
                    curval.append(("A","absent"))
                elif lbl == "AC":
                    curval.append(("AC","present"))
                else:
                    curval.append(("--",None))

                # Convert back to tuple and reassign
                stdAtdlist[res]["values"][ind] = curval
                
            # else:
            #     print("not found" , formatted_date)
                
                

            
        
                
        
        context={
            'values':values,
            'subjects':subjects,
            'attendanceData':attendanceData,
            'computed_range':computed_range,
            'stdAtdlist':stdAtdlist,
        
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
    
    
    
def dateHash(date):
    #convert the date to an integer so that it can be compared , an earlier date should be less than a later date
    return int(date[0:2])+int(date[3:5])*30+int(date[6:])*365
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
        # print(subjects)
        # print(type(subjects))
        subIndex={
            
        }
        for i in range(len(subjects)):
            change_name(subjects[i])
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
                
        
        stdAtdlist = ACmapping(stdAtdlist,user_id,access_token,contextid,rx,subIndex)

            
        
                
        
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



def ACmapping(stdAtdlist , user_id , access_token , contextid , rx , subIndex):
    print("AC mapping")
    AC_ENDPOINT = "https://akgecerp.edumarshal.com/api/StudentAttendanceEventMapping"
    ac_url = f"{AC_ENDPOINT}?OnlyBatch=1&userId={user_id}"
    try:
        response = requests.get(
            ac_url,
            headers={
                'Authorization': f'Bearer {access_token}',
                'X-UserId': user_id,
                'X-ContextId': contextid,
                'X-RX': rx
            }
        )
        if response.status_code != 200:
            print("Failed to fetch AC data")
            return stdAtdlist
        ac_data = response.json()
        new_ac_data = []
        print("AC data fetched")
        for data in ac_data:
            # print(data["studentId"], " " , user_id)
            # print(type(data["studentId"]), " " , type(user_id))
            if data["studentId"] == int(user_id):
                # print(data["studentId"], " " , user_id)
                new_ac_data.append(data)
                # print(data)
                
        

        for data in new_ac_data:
            # print(data)
        
            
            #fir date ko apni format me convert karna hai
            rawdate = data["eventDate"]
            parsed_date = datetime.strptime(rawdate, "%Y-%m-%dT%H:%M:%S")
            formatted_date = parsed_date.strftime("%d-%m-%y")
            
            
            
            #bindary search to find the current data.date
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
                ind = subIndex[data["subjectId"]]
                data_val = data["title"]
                sub_attendance_list = stdAtdlist[res]["values"][ind]
                new_list = []
                flag = 0
                for lecture in sub_attendance_list:
                    
                    #convert the tuple to list
                    lecture = list(lecture)
                    if flag == 0 and lecture[0] == "P":
                        lecture[0] = data_val
                        flag = 1
                    
                        
                        
                        
                    #convert the list to tuple
                    lecture = tuple(lecture)
                    new_list.append(lecture)
                    
                stdAtdlist[res]["values"][ind] = new_list
        return stdAtdlist
    except Exception as e:
        print("AC data not fetched" , e)
        
    
                
    #debug print
    # for i in range(len(stdAtdlist)):
    #     print(stdAtdlist[i]["date"]," ",stdAtdlist[i]["values"])
        
            
        return stdAtdlist
                    
                
                
       
       
def change_name(subject):
    if subject["name"]=="DATABASE  MANAGEMENT SYSTEM":
        subject["name"]="DBMS"  
    elif subject["name"]=="Design and Analysis of  Algorithm":
        subject["name"]="DAA"
    elif subject["name"]=="Database Management System  Lab":
        subject["name"]="DBMS lab"
    elif subject["name"]=="Design and Analysis of Algorithm  Lab":
        subject["name"]="DAA lab"
    elif subject["name"]=="Artificial Intelligence_Lab":
        subject["name"]="AI lab"
    elif subject["name"]=="Artificial_Intelligence":
        subject["name"]="AI"
    elif subject["name"]=="CLOUD   COUMPTING":
        subject["name"]="CC"
    
    

PDP_ENDPOINT="https://akgecerp.edumarshal.com/api/TransportAttendanceReport"
from Authentication.models import TokenModel,UserModel
def get_pdp_attendance(request):
    
    try:
        if not request.session.get('user_id'):
            messages.error(request, 'You are not logged in Clear your cookies/cache and login again')
            return render(request, 'authentication/login.html')
        
        user_id = request.session.get('user_id')
        access_token = request.session.get('access_token')
        contextid = request.session.get('X-ContextId')
        rx = request.session.get('X-RX')
        if not request.session.get('X_token'):
            #yaha pe pahle database me se X_token fetch kar lenge user_id ke basis pe fir use session me save kar denge
            
            token_data = TokenModel.objects.get(user_id=user_id)
            user_data = UserModel.objects.get(user_id=user_id)
            x_token = token_data.x_token
            admission_number = user_data.admission_number
            request.session['admission_number'] = admission_number
            request.session['X_token'] = x_token
        x_token = request.session.get('X_token')
        admission_number = request.session.get('admission_number')
        pdp_url = f"{PDP_ENDPOINT}?admissionNumber={admission_number}&type=7"
        response = requests.get(
            pdp_url,
            headers={
                'Authorization': f'Bearer {access_token}',
                'X-UserId': user_id,
                'X-ContextId': contextid,
                'X-RX': rx,
                'X-Token': x_token
            }
        )
        if response.status_code != 200:
            messages.error(request, 'Failed to fetch PDP attendance data')
            return HttpResponseBadRequest
        pdp_data = response.json()
        values = []
        for i in range(0,len(pdp_data),2):
            cur={
                
            }
            att = []
            date = pdp_data[i]["attendanceDate"]
            date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
            date = date.strftime("%d-%m-%y")
            cur["date"] = date
            # print(type(pdp_data[i]["isInAbsent"]))
            if pdp_data[i]["isInAbsent"]==True:
                att.append(("A","absent"))
            else:
                att.append(("P","present"))
                
                
            if pdp_data[i+1]["isInAbsent"]==True:
                att.append(("A","absent"))
            else:
                att.append(("P","present"))
            cur["label"] = att
            values.append(cur)
        
        totallectures=0
        totalpresent=0
        for it in values:
            for label in it["label"]:
                totallectures+=1
                if label[0]=="P":
                    totalpresent+=1
        totalabsent=totallectures-totalpresent
        Overallpercentage = int((totalpresent/totallectures)*100)
        context={
            "values":values,
            "totallectures":totallectures,
            "totalpresent":totalpresent,
            "totalabsent":totalabsent,
            "Overallpercentage":Overallpercentage
        }
        
        return render(request, 'attendance/pdp.html', context=context)
    
    except Exception as e:
        messages.error(request, str(e))
        print("data not fetched" , e)
        return render(request, 'attendance/pdp.html')
        
       
    
                 
    
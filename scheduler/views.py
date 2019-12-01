from django.shortcuts import render
from backend_code import db_query_function

def homepage(request):
   return render(request, 'homepage.html')


def search(request):
   if request.method == 'POST':
       list1 =[]
       list1_first = request.POST.getlist('coursename')
       for element in list1_first:
           if element!='':
               list1.append(element)


       list2 = request.POST.getlist('weekday_select')
       list3 = request.POST.getlist('campus_Radios')


       if len(list2)==0:
           list2 =['1','2','3','4','5']


       list = db_query_function.course_combination_func(list1,list2,list3)

       if len(list)==0:
           return render(request, 'no_result.html')

       return render(request, 'result_page.html', {"list": list})
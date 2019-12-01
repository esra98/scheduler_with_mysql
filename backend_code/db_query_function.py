import itertools
import mysql.connector

def db_query_func(course_code_list, days_selected_list, campus ):
    mydb = mysql.connector.connect(

        host="localhost",
        user="scraping_sample_user",
        password="I7ZZGUpaHOHJIIZo",
        database="itu_sis_db"
    )

    courses_list = []
    courses = course_code_list
    campus = campus
    days_selected = days_selected_list
    days = []
    if '1' in days_selected:
        days.append('Pazartesi')
    if '2' in days_selected:
        days.append('Salı')
    if '3' in days_selected:
        days.append('Çarşamba')
    if '4' in days_selected:
        days.append('Perşembe')
    if '5' in days_selected:
        days.append('Cuma')

    for course in course_code_list:
        courses_list_sub = []
        mycursor = mydb.cursor()
        query1 = ("SELECT * FROM course_info_db2 WHERE course_code=%s ")
        course = course
        mycursor.execute(query1, (course,))
        for course in mycursor.fetchall():
            if course[15] == campus[0]:
                days_course = (str(course[5]).split())
                if all(x in days for x in days_course):
                    courses_list_sub.append([course[0],course[14]])
        courses_list.extend([courses_list_sub])
    return courses_list

def course_combination_func(list1,list2,list3):
    potential_schedules = []  # cnr'lardan olujşan liste
    lists= db_query_func(list1,list2,list3)
    for combination in itertools.product(*lists):
        cnr_total= [el[0] for el in combination]
        slots_total = ','.join([el[1] for el in combination])
        slots_total= slots_total.split(",")
        if len(slots_total) == len(set(slots_total)):
            potential_schedules.append(cnr_total)
    return (potential_schedules)

        


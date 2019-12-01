"""www.sis.itu.edu.tr adresindeki derslerle ilgili bilgileri(cnr, ders adı, saati, yeri, hocası gibi) ayrı bir mysql veritabanına kopyalar."""

from bs4 import BeautifulSoup
import requests
import mysql.connector
import time


### aşağıdaki fonksiyon ders kodlarından(AKM, ATA gibi) oluşan bir listeyi loopa sokarak ilgili ders kodundaki tüm dersler(AKM 204 gibi) için tek tek bilgileri mysql'e aktarır.
def generate_courseinfo_db():
    course_code_list = ["AKM", "ATA", "ALM", "BEB", "BED", "BEN", "BIL", "BIO", "BLG", "BLS", "BUS", "CAB", "CEV",
                        "CHE", "CHZ", "CIE", "CIN", "CMP", "COM", "DAN", "DEN", "DFH", "DGH", "DNK", "DUI", "EAS",
                        "ECO", "ECN", "EHA", "EHB", "EHN", "EKO", "ELE", "ELH", "ELK", "ELT", "END", "ENE", "ENG",
                        "ENR", "ESL", "ESM", "ETK", "EUT", "FIZ", "FRA", "FZK", "GED", "GEM", "GEO", "GID", "GLY",
                        "GMI", "GMK", "GSB", "GSN", "GUV", "GVT", "HUK", "HSS", "ICM", "ILT", "IML", "ING", "INS",
                        "ISE", "ISH", "ISL", "ISP", "ITA", "ITB", "JDF", "JEF", "JEO", "JPN", "KIM", "KMM", "KMP",
                        "KON", "LAT", "MAD", "MAK", "MAL", "MAT", "MEK", "MEN", "MET", "MCH", "MIM", "MKN", "MST",
                        "MTM", "MOD", "MRE", "MRT", "MTH", "MTK", "MTO", "MTR", "MUH", "MUK", "MUT", "MUZ", "NAE",
                        "NTH", "PAZ", "PEM", "PET", "PHE", "PHY", "RES", "RUS", "SBP", "SEN", "SES", "SNT", "SPA",
                        "STA", "STI", "TDW", "TEB", "TEK", "TEL", "TER", "TES", "THO", "TRZ", "TUR", "UCK", "ULP",
                        "UZB", "YTO"]

    Ayazaga = ['DEP', 'BEB', 'DMB', 'EEB', 'FEB', 'DDB', 'HVZ', 'INB', 'KSB',
               'KMB', 'KORT', 'MED', 'MEDB', 'MDB', 'MOB', 'PYB', 'RSLN-M',
               'SLN-M', 'SDKM', 'SMB', 'STD', 'SYM', 'UUB', 'UZEM', 'YDB',
               'MOBGAM', 'ENB', 'HLB']
    Macka=['DIB','ISB','MIAB','TMB']
    Tuzla=['DZB']
    Gumussuyu=['MKB','SLN-G']
    Taskısla=['MMB']



    mydb = mysql.connector.connect(

        host="localhost",
        user="scraping_sample_user",
        password="I7ZZGUpaHOHJIIZo",
        database="itu_sis_db"
    )
    mycursor = mydb.cursor()
    for course_code in course_code_list:
        url = "http://www.sis.itu.edu.tr/tr/ders_programlari/LSprogramlar/prg.php?fb=" + course_code
        try:
            r= requests.get(url)
        except Exception:
            # sleep for a bit in case that helps
            time.sleep(3)
            # try again
            r= requests.get(url)
        source = BeautifulSoup(r.content, "lxml")
        source = source.findAll("tr")
        ### request ile ilk elementi sütun başlıkları, diğer elemanları tek tek derslerle ilgili bilgileri içeren HTML kodundan oluşan bir liste çekiyorum.
        ### ilk dört eleman ve son eleman stil ile ilgili başlıklardan oluştuğu için onlara ihtiyacım yok, çıkartıyorum.
        source.pop(0)
        source.pop(0)
        source.pop(0)
        source.pop(0)
        source.pop()
        ### aşağıdaki kısımda derslerle ilgili istediğim bilgileri tek tek kendi mysql db'ma kaydediyorum.
        for course in source:
            CNR = course.find("td").text
            course_code = course.select("td:nth-of-type(2)")[0].text
            course_title = course.select("td:nth-of-type(3)")[0].text
            instructor = course.select("td:nth-of-type(4)")[0].text
            building = course.select("td:nth-of-type(5)")[0].text[:3]
            course_day = course.select("td:nth-of-type(6)")[0].text
            course_slot = str(course.select("td:nth-of-type(7)")[0].text)
            course_slot = course_slot[0:-1]
            room = course.select("td:nth-of-type(8)")[0].text
            capacity = course.select("td:nth-of-type(9)")[0].text
            enrolled = course.select("td:nth-of-type(10)")[0].text
            reservation = course.select("td:nth-of-type(11)")[0].text
            major_restriction = course.select("td:nth-of-type(12)")[0].text
            prerequisites = course.select("td:nth-of-type(13)")[0].text
            class_restriction = course.select("td:nth-of-type(14)")[0].text
            campus= ''
            ####binanın koduna göre hangi kampüste olduğunu da mysql table'ına ekleyelim.
            if building in Ayazaga:
                campus= 'Ayazaga'
            if building in Taskısla:
                campus= 'Taskısla'
            if building in Gumussuyu:
                campus= 'Gumussuyu'
            if building in Tuzla:
                campus = 'Tuzla'
            if building in Macka:
                campus= 'Macka'
            course_time_code = []
             ###course_slot diye adlandırdığım variable'ın işlevi pazartesi 8.30'dan cuma 17.30'a kadar...
            ### bütün ders saatlerine 1'den 50'ye kadar numara verip her ders için tek tek bu kodu hesaplatmak.
            ###istenilen derslerin istenilen günlerde olduğu çakışma vermeyen bütün olası programları veren bir proje olduğu için tek tek gün ve saat kontrolü yerine...
            ### bu slotları kontrol ederek çakışma olup olmadığını ya da dersin gününün istediğim günlerde olup olmadığını kontrol edeceğim.
            if len(course_day) > 10 or 'Salı Cuma ' in course_day:
                if course_day.startswith("Pa"):
                    if course_slot.startswith("08"):
                        course_time_code.extend([1, 2])
                    if course_slot.startswith("09"):
                        course_time_code.extend([2, 3])
                    if course_slot.startswith("10"):
                        course_time_code.extend([3, 4])
                    if course_slot.startswith("11"):
                        course_time_code.extend([4, 5])
                    if course_slot.startswith("12"):
                        course_time_code.extend([5, 6])
                    if course_slot.startswith("13"):
                        course_time_code.extend([6, 7])
                    if course_slot.startswith("14"):
                        course_time_code.extend([7, 8])
                    if course_slot.startswith("15"):
                        course_time_code.extend([8, 9])
                    if "Salı" in course_day:
                        if course_slot.endswith("1029"):
                            course_time_code.extend([11, 12])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([12, 13])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([13, 14])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([14, 15])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([15, 16])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([16, 17])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([17, 18])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([18, 19])
                    if "Çarşamba" in course_day:
                        if course_slot.endswith("1029"):
                            course_time_code.extend([21, 22])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([22, 23])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([23, 24])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([24, 25])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([25, 26])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([26, 27])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([27, 28])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([28, 29])
                    if "Perşembe" in course_day:
                        if course_slot.endswith("1029"):
                            course_time_code.extend([31, 32])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([32, 33])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([33, 34])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([34, 35])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([35, 36])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([36, 37])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([37, 38])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([38, 39])
                    if "Cuma" in course_day:
                        if course_slot.endswith("1029"):
                            course_time_code.extend([41, 42])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([42, 43])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([43, 44])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([44, 45])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([45, 46])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([46, 47])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([47, 48])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([48, 49])

                if course_day.startswith("Sa"):
                    if course_slot.startswith("08"):
                        course_time_code.extend([11, 12])
                    if course_slot.startswith("09"):
                        course_time_code.extend([12, 13])
                    if course_slot.startswith("10"):
                        course_time_code.extend([13, 14])
                    if course_slot.startswith("11"):
                        course_time_code.extend([14, 15])
                    if course_slot.startswith("12"):
                        course_time_code.extend([15, 16])
                    if course_slot.startswith("13"):
                        course_time_code.extend([16, 17])
                    if course_slot.startswith("14"):
                        course_time_code.extend([17, 18])
                    if course_slot.startswith("15"):
                        course_time_code.extend([18, 19])
                    if "Pazartesi" in course_day:
                        if course_slot.endswith("1029"):
                            course_time_code.extend([1, 2])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([2, 3])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([3, 4])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([4, 5])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([5, 6])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([6, 7])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([7, 8])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([8, 9])
                    if "Çarşamba" in course_day:
                        if course_slot.endswith("1029"):
                            course_time_code.extend([21, 22])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([22, 23])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([23, 24])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([24, 25])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([25, 26])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([26, 27])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([27, 28])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([28, 29])
                    if "Perşembe" in course_day:
                        if course_slot.endswith("1:29"):
                            course_time_code.extend([31, 32])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([32, 33])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([33, 34])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([34, 35])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([35, 36])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([36, 37])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([37, 38])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([38, 39])
                    if "Cuma" in course_day:
                        if course_slot.endswith("1029"):
                            course_time_code.extend([41, 42])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([42, 43])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([43, 44])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([44, 45])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([45, 46])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([46, 47])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([47, 48])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([48, 49])
                if course_day.startswith("Ça"):
                    if course_slot.startswith("8"):
                        course_time_code.extend([21, 22])
                    if course_slot.startswith("9"):
                        course_time_code.extend([22, 23])
                    if course_slot.startswith("10"):
                        course_time_code.extend([23, 24])
                    if course_slot.startswith("11"):
                        course_time_code.extend([24, 25])
                    if course_slot.startswith("12"):
                        course_time_code.extend([25, 26])
                    if course_slot.startswith("13"):
                        course_time_code.extend([26, 27])
                    if course_slot.startswith("14"):
                        course_time_code.extend([27, 28])
                    if course_slot.startswith("15"):
                        course_time_code.extend([28, 29])
                    if "Pazartesi" in course_day:
                        if course_slot.endswith("1029"):
                            course_time_code.extend([1, 2])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([2, 3])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([3, 4])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([4, 5])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([5, 6])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([6, 7])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([7, 8])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([8, 9])
                    if "Salı" in course_day:
                        if course_slot.endswith("1029"):
                            course_time_code.extend([11, 12])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([12, 13])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([13, 14])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([14, 15])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([15, 16])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([16, 17])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([17, 18])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([18, 19])
                    if "Perşembe" in course_day:
                        if course_slot.endswith("1029"):
                            course_time_code.extend([31, 32])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([32, 33])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([33, 34])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([34, 35])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([35, 36])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([36, 37])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([37, 38])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([38, 39])
                    if "Cuma" in course_day:
                        if course_slot.endswith("1029"):
                            course_time_code.extend([41, 42])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([42, 43])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([43, 44])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([44, 45])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([45, 46])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([46, 47])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([47, 48])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([48, 49])
                if course_day.startswith("Pe"):
                    if course_slot.startswith("08"):
                        course_time_code.extend([31, 32])
                    if course_slot.startswith("09"):
                        course_time_code.extend([32, 33])
                    if course_slot.startswith("10"):
                        course_time_code.extend([33, 34])
                    if course_slot.startswith("11"):
                        course_time_code.extend([34, 35])
                    if course_slot.startswith("12"):
                        course_time_code.extend([35, 36])
                    if course_slot.startswith("13"):
                        course_time_code.extend([36, 37])
                    if course_slot.startswith("14"):
                        course_time_code.extend([37, 38])
                    if course_slot.startswith("15"):
                        course_time_code.extend([38, 39])
                    if "Pazartesi" in course_day:
                        if course_slot.endswith("1029"):
                            course_time_code.extend([1, 2])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([2, 3])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([3, 4])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([4, 5])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([5, 6])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([6, 7])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([7, 8])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([8, 9])
                    if "Salı" in course_day:
                        if course_slot.endswith("1029"):
                            course_time_code.extend([11, 12])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([12, 13])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([13, 14])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([14, 15])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([15, 16])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([16, 17])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([17, 18])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([18, 19])
                    if "Çarşamba" in course_day:
                        if course_slot.endswith("1029"):
                            course_time_code.extend([31, 32])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([32, 33])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([33, 34])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([34, 35])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([35, 36])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([36, 37])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([37, 38])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([38, 39])
                    if "Cuma" in course_day:
                        if course_slot.endswith("1029"):
                            course_time_code.extend([41, 42])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([42, 43])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([43, 44])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([44, 45])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([45, 46])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([46, 47])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([47, 48])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([48, 49])
                if course_day.startswith("Cu"):
                    if course_slot.startswith("8"):
                        course_time_code.extend([41, 42])
                    if course_slot.startswith("9"):
                        course_time_code.extend([42, 43])
                    if course_slot.startswith("10"):
                        course_time_code.extend([43, 44])
                    if course_slot.startswith("11"):
                        course_time_code.extend([44, 45])
                    if course_slot.startswith("12"):
                        course_time_code.extend([45, 46])
                    if course_slot.startswith("13"):
                        course_time_code.extend([46, 47])
                    if course_slot.startswith("14"):
                        course_time_code.extend([47, 48])
                    if course_slot.startswith("15"):
                        course_time_code.extend([48, 49])
                    if "Pazartesi" in course_day:
                        if course_slot.endswith("1029"):
                            course_time_code.extend([1, 2])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([2, 3])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([3, 4])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([4, 5])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([5, 6])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([6, 7])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([7, 8])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([8, 9])
                    if "Salı" in course_day:
                        if course_slot.endswith("1029"):
                            course_time_code.extend([11, 12])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([12, 13])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([13, 14])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([14, 15])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([15, 16])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([16, 17])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([17, 18])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([18, 19])
                    if "Çarşamba" in course_day:
                        if course_slot.endswith("1029"):
                            course_time_code.extend([31, 32])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([32, 33])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([33, 34])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([34, 35])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([35, 36])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([36, 37])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([37, 38])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([38, 39])
                    if "Perşembe" in course_day:

                        if course_slot.endswith("1029"):
                            course_time_code.extend([31, 32])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([32, 33])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([33, 34])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([34, 35])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([35, 36])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([36, 37])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([37, 38])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([38, 39])
            else:

                if course_day.startswith("Pa"):
                    if course_slot.startswith("08"):
                        if course_slot.endswith("0929"):
                            course_time_code.extend([1])
                        if course_slot.endswith("1029"):
                            course_time_code.extend([1, 2])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([1, 2, 3])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([1, 2, 3,4])
                    if course_slot.startswith("09"):
                        if course_slot.endswith("1029"):
                            course_time_code.extend([2])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([2, 3])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([2, 3, 4])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([2, 3, 4,5])
                    if course_slot.startswith("10"):
                        if course_slot.endswith("1129"):
                            course_time_code.extend([3])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([3, 4])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([3, 4, 5])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([3, 4, 5,6])
                    if course_slot.startswith("11"):
                        if course_slot.endswith("1229"):
                            course_time_code.extend([4])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([4, 5])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([4, 5, 6])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([4, 5, 6,7])
                    if course_slot.startswith("12"):
                        if course_slot.endswith("1329"):
                            course_time_code.extend([5])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([5, 6])
                        if course_slot.endswith("1529"):
                            course_time_code = [5, 6, 7]
                        if course_slot.endswith("1629"):
                            course_time_code = [5, 6, 7,8]
                    if course_slot.startswith("13"):
                        if course_slot.endswith("1429"):
                            course_time_code = [6]
                        if course_slot.endswith("1529"):
                            course_time_code = [6, 7]
                        if course_slot.endswith("1629"):
                            course_time_code = [6, 7, 8]
                        if course_slot.endswith("1729"):
                            course_time_code = [6, 7, 8,9]
                    if course_slot.startswith("14"):
                        if course_slot.endswith("1529"):
                            course_time_code.extend([7])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([7, 8])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([7, 8, 9])
                    if course_slot.startswith("15"):
                        if course_slot.endswith("1629"):
                            course_time_code.extend([8])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([8, 9])
                    if course_slot.startswith("16"):
                        if course_slot.endswith("17:29"):
                            course_time_code = [9]

                if course_day.startswith("Sa"):
                    if course_slot.startswith("08"):
                        if course_slot.endswith("0929"):
                            course_time_code.extend([11])
                        if course_slot.endswith("1029"):
                            course_time_code.extend([11, 12])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([11, 12, 13])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([11, 12, 13,14])
                    if course_slot.startswith("09"):
                        if course_slot.endswith("1029"):
                            course_time_code.extend([12])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([12, 13])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([12, 13, 14])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([12, 13, 14,15])
                    if course_slot.startswith("10"):
                        if course_slot.endswith("1129"):
                            course_time_code.extend([13])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([13, 14])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([13, 14, 15])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([13, 14, 15,16])
                    if course_slot.startswith("11"):
                        if course_slot.endswith("1229"):
                            course_time_code.extend([14])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([14, 15])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([14, 15, 16])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([14, 15, 16,17])
                    if course_slot.startswith("12"):
                        if course_slot.endswith("1329"):
                            course_time_code.extend([15])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([15, 16])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([15, 16, 17])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([15, 16, 17,18])
                    if course_slot.startswith("13"):
                        if course_slot.endswith("1429"):
                            course_time_code.extend([16])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([16, 17])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([16, 17, 18])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([16, 17, 18,19])
                    if course_slot.startswith("14"):
                        if course_slot.endswith("1529"):
                            course_time_code.extend([17])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([17, 18])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([17, 18, 19])
                    if course_slot.startswith("15"):
                        if course_slot.endswith("1629"):
                            course_time_code.extend([18])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([18, 19])
                    if course_slot.startswith("16"):
                        if course_slot.endswith("1729"):
                            course_time_code.extend([19])

                if course_day.startswith("Ça"):
                    if course_slot.startswith("08"):
                        if course_slot.endswith("0929"):
                            course_time_code.extend([21])
                        if course_slot.endswith("1029"):
                            course_time_code.extend([21, 22])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([21, 22, 23])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([21, 22, 23,24])
                    if course_slot.startswith("09"):
                        if course_slot.endswith("1029"):
                            course_time_code.extend([22])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([22, 23])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([22, 23, 24])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([22, 23, 24,25])
                    if course_slot.startswith("10"):
                        if course_slot.endswith("1129"):
                            course_time_code.extend([23])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([23, 24])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([23, 24, 25])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([23, 24, 25,26])
                    if course_slot.startswith("11"):
                        if course_slot.endswith("1229"):
                            course_time_code.extend([24])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([24, 25])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([24, 25, 26])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([24, 25, 26,27])
                    if course_slot.startswith("12"):
                        if course_slot.endswith("1329"):
                            course_time_code.extend([25])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([25, 26])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([25, 26, 27])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([25, 26, 27,28])
                    if course_slot.startswith("13"):
                        if course_slot.endswith("1429"):
                            course_time_code.extend([26])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([26, 27])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([26, 27, 28])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([26, 27, 28,29])
                    if course_slot.startswith("14"):
                        if course_slot.endswith("1529"):
                            course_time_code.extend([27])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([27, 28])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([27, 28, 29])
                    if course_slot.startswith("15"):
                        if course_slot.endswith("1629"):
                            course_time_code.extend([28])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([28, 29])
                    if course_slot.startswith("16"):
                        if course_slot.endswith("1729"):
                            course_time_code.extend([29])

                if course_day.startswith("Pe"):
                    if course_slot.startswith("08"):
                        if course_slot.endswith("0929"):
                            course_time_code.extend([31])
                        if course_slot.endswith("1029"):
                            course_time_code.extend([31, 32])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([31, 32, 33])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([31, 32, 33,34])
                    if course_slot.startswith("09"):
                        if course_slot.endswith("1029"):
                            course_time_code.extend([32])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([32, 33])
                        if course_slot.endswith("1229"):
                            course_time_code = [32, 33, 34]
                        if course_slot.endswith("1329"):
                            course_time_code = [32, 33, 34,35]
                    if course_slot.startswith("10"):
                        if course_slot.endswith("1129"):
                            course_time_code.extend([33])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([33, 34])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([33, 34, 35])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([33, 34, 35,36])
                    if course_slot.startswith("11"):
                        if course_slot.endswith("1229"):
                            course_time_code.extend([34])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([34, 35])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([34, 35, 36])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([34, 35, 36,37])
                    if course_slot.startswith("12"):
                        if course_slot.endswith("1329"):
                            course_time_code.extend([35])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([35, 36])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([35, 36, 37])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([35, 36, 37,38])
                    if course_slot.startswith("13"):
                        if course_slot.endswith("1429"):
                            course_time_code.extend([36])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([36, 37])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([36, 37, 38])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([36, 37, 38,39])
                    if course_slot.startswith("14"):
                        if course_slot.endswith("1529"):
                            course_time_code.extend([37])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([37, 38])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([37, 38, 39])
                    if course_slot.startswith("15"):
                        if course_slot.endswith("1629"):
                            course_time_code.extend([38])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([38, 39])
                    if course_slot.startswith("16"):
                        if course_slot.endswith("1729"):
                            course_time_code.extend([39])

                if course_day.startswith("Cu"):
                    if course_slot.startswith("08"):
                        if course_slot.endswith("0929"):
                            course_time_code.extend([41])
                        if course_slot.endswith("1029"):
                            course_time_code.extend([41, 42])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([41, 42, 43])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([41, 42, 43,44])
                    if course_slot.startswith("09"):
                        if course_slot.endswith("1029"):
                            course_time_code.extend([42])
                        if course_slot.endswith("1129"):
                            course_time_code.extend([42, 43])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([42, 43, 44])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([42, 43, 44,45])
                    if course_slot.startswith("10"):
                        if course_slot.endswith("1129"):
                            course_time_code.extend([43])
                        if course_slot.endswith("1229"):
                            course_time_code.extend([43, 44])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([43, 44, 45])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([43, 44, 45,46])
                    if course_slot.startswith("11"):
                        if course_slot.endswith("1229"):
                            course_time_code.extend([44])
                        if course_slot.endswith("1329"):
                            course_time_code.extend([44, 45])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([44, 45, 46])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([44, 45, 46,47])
                    if course_slot.startswith("12"):
                        if course_slot.endswith("1329"):
                            course_time_code.extend([45])
                        if course_slot.endswith("1429"):
                            course_time_code.extend([45, 46])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([45, 46, 47])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([45, 46, 47,48])
                    if course_slot.startswith("13"):
                        if course_slot.endswith("1429"):
                            course_time_code.extend([46])
                        if course_slot.endswith("1529"):
                            course_time_code.extend([46, 47])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([46, 47, 48])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([46, 47, 48,49])
                    if course_slot.startswith("14"):
                        if course_slot.endswith("1529"):
                            course_time_code.extend([47])
                        if course_slot.endswith("1629"):
                            course_time_code.extend([47, 48])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([47, 48, 49])
                        if course_slot.endswith("1659"):
                            course_time_code.extend([47, 48, 49])
                    if course_slot.startswith("15"):
                        if course_slot.endswith("1629"):
                            course_time_code.extend([48])
                        if course_slot.endswith("1729"):
                            course_time_code.extend([48, 49])
                    if course_slot.startswith("16"):
                        if course_slot.endswith("1729"):
                            course_time_code.extend([49])
            print(course_day)
            print(course_code_list)
            print(campus)
            print(course_day)
            course_time_code = ','.join(map(str, course_time_code))
            ### aşağıda parantez içindeki variablelar benim mysql db'mdeki sütunlar
            sql = "INSERT INTO course_info_db2 (CNR, course_code, course_title, instructor, building, campus, course_day, course_time, room,capacity,enrolled,reservation, major_restriction, prerequisites, class_restriction, course_time_code) VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s,%s)"
            ### websitesinden elde ettiğim bilgileri kendi db'ma aktarıyorum.
            val = [
                (
                CNR, course_code, course_title, instructor, building, campus , course_day, course_slot, room, capacity, enrolled,
                reservation, major_restriction, prerequisites, class_restriction, course_time_code),
            ]
            mycursor.executemany(sql, val)
            ### ve kaydediyorum
            mydb.commit()
            
generate_courseinfo_db()
## database'i oluşturmak yukarıda yazdığım "generate_courseinfo_db" fonksiyonunu bir kere çalıştırıyorum.
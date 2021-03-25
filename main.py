import re, requests, tools as t, time

def extractContent(niz):#oblika '<>'
    return re.sub(r'<.+?>','',niz)


class Event:
    def __init__(self,EventID):
        self.EventID = EventID
        
        #kraj in država iz linka html
        html = requests.get(f'https://www.fis-ski.com/DB/general/event-details.html?sectorcode=JP&eventid={EventID}').text
        regex = re.search(r'<h1 class="heading heading_l2 heading_off-sm-style heading_plain event-header__name">.+</h1>',html).group()
        niz = re.sub(r'<.+?>','',regex)
        kraj,država = niz.split('(')
        self.država = država[:-1]
        self.kraj = kraj[:-1]
        
        #compIDS + genders
        tabGenders = []
        self.tabComps = []
        tagsOfComps = re.findall(r'<a class="g-lg-1 g-md-1 g-sm-2 hidden-sm-down justify-left" href=".+" target="_self">',html)
        urlsToComps = list(map(t.ExtractURL,tagsOfComps))
        genders = re.findall('<div class="gender__item gender__item_\w">\w</div>',html)
        for g in genders:
            tabGenders.append(g.split('"')[-1][1])
        for i in range(len(urlsToComps)):
            self.tabComps.append(Competition(int(urlsToComps[i].split('raceid=')[1]),tabGenders[i]))
        
class Competition:
    def __init__(self,raceID,gender):
        self.raceID = raceID
        self.gender = gender
        html = requests.get(f'https://www.fis-ski.com/DB/general/results.html?sectorcode=JP&raceid={raceID}').text
        regex = re.search(r'<div class="event-header__subtitle">.+</div>',html).group()
        self.category = re.sub(r'<.+?>','',regex)
        
        #podatki o rezultatih tekmovalcev
        self.tabRez = []
        regex = re.findall(r'<div class="g-lg-1 g-md-1 g-sm-1 justify-right hidden-xs pr-1 gray">[0-9]+?</div>',html)
        tabBib = list(map(extractContent,regex))
        
        regex = re.findall(r'<div class="g-lg-2 g-md-2 g-sm-2 hidden-xs justify-right gray pr-1">[0-9]+?</div>',html)
        tabfiscode = list(map(extractContent,regex))
        
        regex = re.findall(r'<div class="g-lg g-md g-sm g-xs justify-left bold">.+?</div>',html)
        tabHumans = list(map(extractContent,regex))
        
        regex = re.findall(r'<div class="g-lg-1 g-md-1 g-sm-2 g-xs-3 justify-left">[0-9]+?</div>',html)
        tabbirth = list(map(extractContent,regex))
        
        regex = re.findall(r'<span class="country__name-short">.+?</span>',html)
        tabcountry = list(map(extractContent,regex))
        
        regex = re.findall(r'<div class="g-lg-2 g-md-2 g-sm-3 g-xs-5 justify-right blue bold ">[0-9]+?\.[0-9]</div>',html)
        tabTotalPoints = list(map(extractContent,regex))
        
        for i in range(len(tabHumans)):
            name = ' '.join(tabHumans[i].split()[1:])
            surname = tabHumans[i].split()[0]
            self.tabRez.append(Result(tabBib[i],tabfiscode[i],name,surname,tabbirth[i],tabcountry[i],tabTotalPoints[i]))
            
class Result:
    def __init__(self,bib,fiscode,name,surname,birth,country,totalPoints,rez1 = None,rez2 = None):
        self.bib = bib
        self.fiscode = fiscode
        self.name = name
        self.surname = surname
        self.birth = birth
        self.country = country
        self.totalPoints = totalPoints
        self.rez1 = rez1
        self.rez2 = rez2

class Athlete:
    pass



'''Glavna stran'''
leto = 2021
html = requests.get(f"https://www.fis-ski.com/DB/ski-jumping/calendar-results.html?eventselection=results&place=&sectorcode=JP&seasoncode={leto}&categorycode=&disciplinecode=&gendercode=&racedate=&racecodex=&nationcode=&seasonmonth=X-{leto}&saveselection=-1&seasonselection=").text

'''Eventi'''
tagsOfEvents = re.findall(r"<a class=\"pr-1 g-lg-1 g-md-1 g-sm-2 hidden-xs justify-left\"  href=\".+?\" target=\"_self\">",html)
urlsToEvents = list(map(t.ExtractURL,tagsOfEvents))
print(urlsToEvents)


time.sleep(.5)
# = re.search(r"https:\/\/.*[0-9]{4}",found)




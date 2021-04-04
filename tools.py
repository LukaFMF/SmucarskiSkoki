import re, requests, os, struct as s, time

def ExtractURL(tag):
    ''' Iz niza, ki vsebuje HTML znacko z URL naslovom izlusci ta URL '''
    return re.search(r"http.+?\"",tag).group()[:-1] # odstranimo zadnji znak, da se znebimo "

def ExtractContent(string):
    ''' Iz niza odstrani HTML znacke in vrne kar ostane '''
    return re.sub(r'<.+?>','',string)

def ExtractArgumentValueFromURL(url,arg):
    ''' Iz URL naslova pridobi vrednost argumetna arg '''
    res = re.search(rf'{arg}=.*\&|{arg}=.*',url)
    if res:
        argStr = res.group()
        
        if argStr[-1] == '&':
            return argStr[len(arg) + 1:-1].strip()
        return argStr[len(arg) + 1:].strip()
    else:
        raise Exception(f"URL \"{url}\" does not contain argument \"{arg}\"!")

class Event:
    def __init__(self,eventId = None):
        if eventId != None:
            self.eventId = eventId
            
            # kraj in drzava s strani
            html = requests.get(f'https://www.fis-ski.com/DB/general/event-details.html?sectorcode=JP&eventid={eventId}').text
            tagLocationCountry = re.search(r'<h1 class="heading heading_l2 heading_off-sm-style heading_plain event-header__name">.+</h1>',html).group()
            location,country = ExtractContent(tagLocationCountry).split('(')

            self.location = location[:-1]
            self.country = country[:-1]
            
            
            self.competitions = []
            tabGenders = []
            tagsOfComps = re.findall(r'<a class="g-lg-1 g-md-1 g-sm-2 hidden-sm-down justify-left" href=".+" target="_self">',html)
            urlsToComps = list(map(ExtractURL,tagsOfComps))
            
            regex = re.findall(r'<div class="g-xs-24 justify-left"><div class="clip">[\w\n\s]+</div>',html)
            self.tabKindsOfComps = list(map(ExtractContent,regex)) #dobimo tabelo oznak tekmovanj npr. 'HS240' ali 'Team HS 140'
            self.tabKindsOfComps = [' '.join(el.split()) for el in self.tabKindsOfComps]
            
            tabOfGenderTags = re.findall('<div class="gender__item gender__item_\w">\w</div>',html)
            for genderTag in tabOfGenderTags:
                tabGenders.append(ExtractContent(genderTag))

            for i in range(len(urlsToComps)):
                if 'Team' in self.tabKindsOfComps[i*2]: #ni ekipna tekma
                    self.competitions.append(teamCompetition(int(ExtractArgumentValueFromURL(urlsToComps[i],"raceid")),tabGenders[i]))
                    
                else: #je ekipna tekma
                    self.competitions.append(Competition(int(ExtractArgumentValueFromURL(urlsToComps[i],"raceid")),tabGenders[i]))
                time.sleep(.25) # nekaj casa pocakamo, da nas streznik ne blokira
        else:
            self.eventId = None
            self.location = None
            self.country = None
            self.competitions = []

        
class Competition:
    def __init__(self,raceId = None,gender = None):
        if raceId != None:
            self.raceId = raceId
            self.gender = gender

            html = requests.get(f'https://www.fis-ski.com/DB/general/results.html?sectorcode=JP&raceid={raceId}').text
            tagCategory = re.search(r'<div class="event-header__subtitle">.+</div>',html).group()
            self.category = ExtractContent(tagCategory)

            html = html.split('<div data-module="cells-join,list-false-links" class="table table_min_height">')[1]
            
            #podatki o rezultatih tekmovalcev
            regex = re.findall(r'<div class="g-lg-1 g-md-1 g-sm-1 justify-right hidden-xs pr-1 gray">[0-9]+?</div>',html)
            tabBib = list(map(ExtractContent,regex))

            regex = re.findall(r'<div class="g-lg-2 g-md-2 g-sm-2 hidden-xs justify-right gray pr-1">[0-9]+?</div>',html)
            tabFisCode = list(map(ExtractContent,regex))

            regex = re.findall(r'<div class="g-lg g-md g-sm g-xs justify-left bold">[\w\n\s\-]+</div>',html)
            tabNames = list(map(ExtractContent,regex))
            tabNames = [name.strip() for name in tabNames] # odstranimo presledke

            regex = re.findall(r'<div class="g-lg-1 g-md-1 g-sm-2 g-xs-3 justify-left">[0-9]+?</div>',html)
            tabBirthYears = list(map(ExtractContent,regex))

            regex = re.findall(r'<span class="country__name-short">.+?</span>',html)
            tabCountry = list(map(ExtractContent,regex))

            regex = re.findall(r'<div class="g-lg-2 g-md-2 g-sm-3 g-xs-5 justify-right blue bold ">[0-9\.\n\s]+</div>',html)
            tabTotalPoints = list(map(ExtractContent,regex))
            tabTotalPoints = [totalPoints.strip() for totalPoints in tabTotalPoints] # odstranimo presledke

            hasPoints1 = re.search(r'Points 1',html) != None
            hasPoints2 = re.search(r'Points 2',html) != None
            if hasPoints1:
                regex = re.findall(r'<div class="g-row justify-right bold">[0-9\.\n\s]+</div>',html)
                tabDistance = list(map(ExtractContent,regex))
                tabDistance = [dist.strip() for dist in tabDistance]

                regex = re.findall(r'<div class="g-lg-24 justify-right bold">[0-9\.\n\s]+</div>',html)
                tabPoints = list(map(ExtractContent,regex))
                tabPoints = [points.strip() for points in tabPoints]
                                
                                
            self.results = []
            for i in range(len(tabNames)):
                # ce so tocke tekmovalca zabelezene potem je rezultat veljaven, drugace pa je bil izkljucen, ali pa sploh ni skocil
                if len(tabTotalPoints[i]) > 0:
                    name = ' '.join(tabNames[i].split()[1:])
                    surname = tabNames[i].split()[0]
                    if not hasPoints1:
                        self.results.append(Result(int(tabFisCode[i]),name,surname,int(tabBirthYears[i]),tabCountry[i],int(tabBib[i]),float(tabTotalPoints[i])))
                    elif hasPoints1 and not hasPoints2:
                        self.results.append(Result(int(tabFisCode[i]),name,surname,int(tabBirthYears[i]),tabCountry[i],int(tabBib[i]),float(tabTotalPoints[i]),float(tabDistance[i]),float(tabPoints[i])))
                    else:
                        if len(tabDistance[2*i + 1]) == 0:
                            self.results.append(Result(int(tabFisCode[i]),name,surname,int(tabBirthYears[i]),tabCountry[i],float(tabTotalPoints[i]),int(tabBib[i]),float(tabDistance[2*i]),float(tabPoints[2*i])))
                        else:
                            self.results.append(Result(int(tabFisCode[i]),name,surname,int(tabBirthYears[i]),tabCountry[i],float(tabTotalPoints[i]),int(tabBib[i]),float(tabDistance[2*i]),float(tabPoints[2*i]),float(tabDistance[2*i + 1]),float(tabPoints[2*i + 1])))
        
        else:
            self.raceId = None
            self.gender = None
            self.category = None
            self.results = []

            
class Result:
    def __init__(self,fiscode,name,surname,birthYear,country = None,totalPoints = None,bib = None,dist1 = None,points1 = None,dist2 = None,points2 = None):
        self.bib = bib
        self.fisCode = fiscode
        self.name = name
        self.surname = surname
        self.birthYear = birthYear
        self.country = country
        self.totalPoints = totalPoints
        self.distance1 = dist1
        self.points1 = points1
        self.distance2 = dist2
        self.points2 = points2

class teamCompetition:
    def __init__(self,raceId = None, gender = None):
        if raceId != None:
            self.raceId = raceId
            self.gender = gender
            
            html = requests.get(f'https://www.fis-ski.com/DB/general/results.html?sectorcode=JP&raceid={raceId}').text
            tagCategory = re.search(r'<div class="event-header__subtitle">.+</div>',html).group()
            self.category = ExtractContent(tagCategory)
            
            html = html.split('<div data-module="cells-join,list-false-links" class="table table_min_height">')[1]
            
            #podatki o rezultatih ekip
            regex = re.findall(r'<div class="g-lg-9 g-md-9 g-sm-5 g-xs-11 justify-left bold">[\w\n\s\-]+</div>',html) 
            tabCountryAndNames = list(map(ExtractContent,regex)) #dobimo tako imena držav, kot vseh tekmovalcev
            tabCountryAndNames = [name.strip() for name in tabCountryAndNames]
            
            regex = re.findall(r'<div class="g-lg-2 g-md-2 g-sm-3 hidden-xs justify-right gray pr-1">[0-9]+?</div>',html)
            tabAllFisCodes = list(map(ExtractContent,regex)) #dobimo vse Fis kode, tudi od tekmovalcev
            
            regex = re.findall(r'<div class="g-lg-2 g-md-2 g-sm-3 g-xs-5 justify-right">[0-9]+\.[0-9]</div>',html)
            tabTotalPoints = list(map(ExtractContent,regex))
            
            tabResultsOfCompetitors = []
            
            tabNames =[]
            tabCountry = []
            country = None
            
            for i in range(len(tabCountryAndNames)): #ločimo imena držav in imena tekmovalcev, ter jim dodamo Fis kode in njihovo državo
                if tabCountryAndNames[i].isupper():#če je niz ves z velikimi črkami potem je država
                    country = tabCountryAndNames[i]
                    tabCountry.append([tabCountryAndNames[i],tabAllFisCodes[i]])
                else:
                    tabNames.append([tabCountryAndNames[i],tabAllFisCodes[i],country])
            
            
            regex = re.findall(r'<div class="g-lg-1 g-md-1 g-sm-2 g-xs-3 justify-left">[0-9]+?</div>',html)
            tabBirthYears = list(map(ExtractContent,regex))
            
            newHtml = html.split('<div class="g-lg-9 g-md-9 g-sm-5 g-xs-11 justify-left bold">')[1:]
            tabSoloResoults = [] #tabela tabel skokov/točk vsakega tekmovalca v ekipi
            for el in newHtml:
                if re.search(r'<span class="country__name-short">\w+?</span>',el) == None:#odstranimo države
                    regex = re.findall(r'<div class="g-lg-2 g-md-2 g-sm-2 justify-right bold hidden-xs">[0-9]*\.[0-9]*</div>',el)
                    tabAllDistAndPoints = list(map(ExtractContent,regex))
                    tabAllDistAndPoints = [el.strip() for el in tabAllDistAndPoints]
                    tabSoloResoults.append(tabAllDistAndPoints)
            if len(tabSoloResoults[0]) < 3 or (tabSoloResoults[0][0] == tabSoloResoults[0][2] and tabSoloResoults[0][3] == tabSoloResoults[0][1]): #bila je samo 1 serija
                for i in range(len(tabNames)):
                    name = ' '.join(tabNames[i][0].split()[1:])
                    surname = tabNames[i][0].split()[0]
                    if tabSoloResoults[i] == []: #tekmovalec nima rezultata
                        tabResultsOfCompetitors.append(Result(int(tabNames[i][1]),name,surname,int(tabBirthYears[i]),tabNames[i][2]))
                    else:
                        tabResultsOfCompetitors.append(Result(int(tabNames[i][1]),name,surname,int(tabBirthYears[i]),tabNames[i][2],None,None,float(tabSoloResoults[i][0]),float(tabSoloResoults[i][1])))
            else:#imamo 2 seriji
                 for i in range(len(tabNames)):
                    name = ' '.join(tabNames[i][0].split()[1:])
                    surname = tabNames[i][0].split()[0]
                    if tabSoloResoults[i] == []: #tekmovalec nima rezultata
                        tabResultsOfCompetitors.append(Result(int(tabNames[i][1]),name,surname,int(tabBirthYears[i]),tabNames[i][2]))
                    else:
                        tabResultsOfCompetitors.append(Result(int(tabNames[i][1]),name,surname,int(tabBirthYears[i]),tabNames[i][2],None,None,float(tabSoloResoults[i][0]),float(tabSoloResoults[i][1]),float(tabSoloResoults[i][2]),float(tabSoloResoults[i][3])))
            
            self.results = []
            NamesPerTeam = int(len(tabNames)/len(tabCountry))#število članov v posamezni ekipi
            for i in range(len(tabCountry)):
                self.results.append(teamResult(tabCountry[i][0],int(tabCountry[i][1]),float(tabTotalPoints[i]),tabResultsOfCompetitors[i*NamesPerTeam:(i+1)*NamesPerTeam]))
                
        else:
            self.raceId = None
            self.gender = None
            self.category = None
            self.results = []

class teamResult:#po posamezni državi
    def __init__(self,country,countryFisCode,TotalPoints,tabResultsOfCompetitors):
        self.country = country
        self.countryFisCode = countryFisCode
        self.totalPoints = TotalPoints
        self.results = tabResultsOfCompetitors 
        
        
class Athlete:
    pass


class DateException(Exception):
    def __init__(self,year,month,day):
        super().__init__(f"Date {year}-{month}-{day} is not a valid!")

class Date:
    def __init__(self,year,month,day):
        if (not isinstance(year,int) or not isinstance(month,int) or not isinstance(day,int) or 
            year < 1950 or month < 1 or month > 12 or day < 1 or day < Date.DaysInMonth(month,year)):
            raise DateException(year,month,day)
            
        self.year = year
        self.month = month
        self.day = day

    def __str__(self):
        return f"{self.year}-{self.month}-{self.day}"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.year},{self.month},{self.day})"

    def ToBytes(self):
        return s.pack("3I",self.year,self.month,self.day)

    @staticmethod
    def FromBytes(dataInBytes):
        year,month,day = s.unpack("3I",dataInBytes)

        return Date(year,month,day)

    @staticmethod
    def IsLeapYear(year):
        if year % 4 != 0:
            return False
        elif year % 100 != 0:
            return True
        elif year % 400 != 0:
            return False
        return True

    @staticmethod
    def DaysInMonth(month,year):
        if month <= 7:
            if month == 2:
                return 29 if IsLeapYear(year) else 28
            return 30 if month % 2 == 0 else 31
        return 31 if month % 2 == 0 else 30

def PackStrToBytes(string):
    ''' Vrne par, ki vsebuje zakodirano dolznino niza in niz sam '''
    length = len(string)
    return s.pack("I",length),s.pack(f"{length}s",bytes(string,encoding = "utf8"))

def WriteEventToFile(event):
    ''' Zapise podani objekt razreda Event v binarno datoteko '''
    thingsToWrite = []

    # zapisemo id, lokacijo in drzavo dogodka
    thingsToWrite.append(s.pack("I",event.eventId))
    thingsToWrite.extend(PackStrToBytes(event.location))
    thingsToWrite.extend(PackStrToBytes(event.country))

    # signaliziramo ali sledi tudi datum, ki nam pove konec dogodka
    # writeEndDate = event.endDate != None
    # thingsToWrite.append(s.pack("?",writeEndDate))

    # thingsToWrite.append(event.startDate.ToBytes())
    # if writeEndDate:
    #   thingsToWrite.append(evenendDate.ToBytes())

    # koliko tekmovanj sledi
    thingsToWrite.append(s.pack("I",len(event.competitions)))
    for competition in event.competitions:
        thingsToWrite.append(s.pack("I",competition.raceId))
        thingsToWrite.append(s.pack("c",bytes(competition.gender,encoding = "utf8")))
        thingsToWrite.extend(PackStrToBytes(competition.category))
        
        # koliko rezultatov sledi
        thingsToWrite.append(s.pack("I",len(competition.results)))
        for result in competition.results:
            thingsToWrite.append(s.pack("I",result.bib))
            thingsToWrite.append(s.pack("I",result.fisCode))
            thingsToWrite.extend(PackStrToBytes(result.name))
            thingsToWrite.extend(PackStrToBytes(result.surname))
            thingsToWrite.append(s.pack("I",result.birthYear))
            thingsToWrite.extend(PackStrToBytes(result.country))
            thingsToWrite.append(s.pack("f",result.totalPoints))

    dat = open(os.path.join("data",f"{event.eventId}.bin"),"wb")
    for dataInBytes in thingsToWrite:
        dat.write(dataInBytes)

    dat.close()

def UnpackStrFromBytes(data,offset):
    ''' Prebere dozino niz in niz na lokaciji offset in vrne ta niz ter nov offset '''
    length = s.unpack("I",data[offset:offset+4])[0] # prebermo dolzino niza
    string = s.unpack(f"{length}s",data[offset+4:offset+length+4])[0].decode()
    return string, offset + length + 4 

def ReadEvent(eventId):
    ''' Prebere dogodek iz diska, ce je na voljo, drugace pa iz spletne strani in ga zapise za naslednijc '''
    # ce vidimo, da je ta dogodek ze shranjen lahko podatke pridobimo iz datotke
    pathToFile = os.path.join("data",f"{eventId}.bin")
    if os.path.exists(pathToFile):
        # preberemo podatke
        dat = open(pathToFile,"rb")
        data = dat.read()
        dat.close()

        event = Event()
        offset = 0

        # preberemo id, lokacijo in drzavo dogodka
        event.eventId = s.unpack("I",data[offset:offset+4])[0]
        offset += 4
        event.location,offset = UnpackStrFromBytes(data,offset)
        event.country,offset = UnpackStrFromBytes(data,offset)

        # stevilo tekmovanj pri dogodku
        numRaces = s.unpack("I",data[offset:offset+4])[0]
        offset += 4
        for _ in range(numRaces):
            competition = Competition()
            competition.raceId = s.unpack("I",data[offset:offset+4])[0]
            offset += 4
            competition.gender = s.unpack("c",data[offset:offset+1])[0].decode()
            offset += 1
            event.category,offset = UnpackStrFromBytes(data,offset)

            # stevilo rezultatov pri tekmovanju
            numResults = s.unpack("I",data[offset:offset+4])[0]
            offset += 4
            for _ in range(numResults):
                bib = s.unpack("I",data[offset:offset+4])[0]
                offset += 4
                fisCode = s.unpack("I",data[offset:offset+4])[0]
                offset += 4
                name,offset = UnpackStrFromBytes(data,offset)
                surname,offset = UnpackStrFromBytes(data,offset)
                birthYear = s.unpack("I",data[offset:offset+4])[0]
                offset += 4
                country,offset = UnpackStrFromBytes(data,offset)
                totalPoints = s.unpack("f",data[offset:offset+4])[0]
                offset += 4

                competition.results.append(Result(fisCode,name,surname,birthYear,country,totalPoints,bib))

            event.competitions.append(competition)

        return event
    else:
        event = Event(eventId)
        # dogodek shranimo, da ob naslednjem zagonu programa ni treba spet dostopati do spletne strani
        WriteToFile(event) 
        return event

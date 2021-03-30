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

			tabOfGenderTags = re.findall('<div class="gender__item gender__item_\w">\w</div>',html)
			for genderTag in tabOfGenderTags:
				tabGenders.append(ExtractContent(genderTag))

			for i in range(len(urlsToComps)):
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
			
			#podatki o rezultatih tekmovalcev
			regex = re.findall(r'<div class="g-lg-1 g-md-1 g-sm-1 justify-right hidden-xs pr-1 gray">[0-9]+?</div>',html)
			tabBib = list(map(ExtractContent,regex))
			
			regex = re.findall(r'<div class="g-lg-2 g-md-2 g-sm-2 hidden-xs justify-right gray pr-1">[0-9]+?</div>',html)
			tabFisCode = list(map(ExtractContent,regex))
			
			regex = re.findall(r'<div class="g-lg g-md g-sm g-xs justify-left bold">[\w\n\s]+</div>',html)
			tabNames = list(map(ExtractContent,regex))
			tabNames = [name.strip() for name in tabNames] # odstranimo presledke
			
			regex = re.findall(r'<div class="g-lg-1 g-md-1 g-sm-2 g-xs-3 justify-left">[0-9]+?</div>',html)
			tabBirthYears = list(map(ExtractContent,regex))
			
			regex = re.findall(r'<span class="country__name-short">.+?</span>',html)
			tabCountry = list(map(ExtractContent,regex))
			
			regex = re.findall(r'<div class="g-lg-2 g-md-2 g-sm-3 g-xs-5 justify-right blue bold ">[0-9\.\n\s]+</div>',html)
			tabTotalPoints = list(map(ExtractContent,regex))
			tabTotalPoints = [totalPoints.strip() for totalPoints in tabTotalPoints] # odstranimo presledke
			
			self.results = []
			for i in range(len(tabNames)):
				# ce so tocke tekmovalca zabelezene potem je rezultat veljaven, drugace pa je bil izkljucen, ali pa sploh ni skocil
				if len(tabTotalPoints[i]) > 0:
					name = ' '.join(tabNames[i].split()[1:])
					surname = tabNames[i].split()[0]
					self.results.append(Result(int(tabBib[i]),int(tabFisCode[i]),name,surname,int(tabBirthYears[i]),tabCountry[i],float(tabTotalPoints[i])))
		else:
			self.raceId = None
			self.gender = None
			self.category = None
			self.results = []

			
class Result:
	def __init__(self,bib,fiscode,name,surname,birthYear,country,totalPoints,rez1 = None,rez2 = None):
		self.bib = bib
		self.fisCode = fiscode
		self.name = name
		self.surname = surname
		self.birthYear = birthYear
		self.country = country
		self.totalPoints = totalPoints
		self.res1 = rez1
		self.res2 = rez2

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
	# 	thingsToWrite.append(evenendDate.ToBytes())

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
			competition.gender = s.unpack("c",data[offset:offset+1])[0]
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

				competition.results.append(Result(bib,fisCode,name,surname,birthYear,country,totalPoints))

			event.competitions.append(competition)

		return event
	else:
		event = Event(eventId)
		# dogodek shranimo, da ob naslednjem zagonu programa ni treba spet dostopati do spletne strani
		WriteToFile(event) 
		return event

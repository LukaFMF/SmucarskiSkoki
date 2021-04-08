import re, requests, os, struct as s, time, copy as c

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

class DateException(Exception):
	def __init__(self,year,month,day):
		super().__init__(f"Date {year}-{month}-{day} is not valid!")

class Date:
	def __init__(self,year,month,day):
		if (not isinstance(year,int) or not isinstance(month,int) or not isinstance(day,int) or 
			year < 1950 or month < 1 or month > 12 or day < 1 or day > Date.DaysInMonth(month,year)):
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
	def FromStr(string):
		# <span class="date__short">Mar 24, 2021</span>
		monthMap = {
			"Jan": 1,
			"Feb": 2,
			"Mar": 3,
			"Apr": 4,
			"May": 5,
			"Jun": 6,
			"Jul": 7,
			"Aug": 8,
			"Sep": 9,
			"Oct": 10,
			"Nov": 11,
			"Dec": 12
		}
		spl = string.split(" ")
		return Date(int(spl[2]),monthMap[spl[0]],int(spl[1][:-1]))

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
				return 29 if Date.IsLeapYear(year) else 28
			return 30 if month % 2 == 0 else 31
		return 31 if month % 2 == 0 else 30

def HillHeightClass(height):
	if height < 85:
		return "XX"
	elif height < 110:
		return "NH"
	elif height < 185:
		return "LH"
	return "FH"

def HillCategory(string):
	if string.startswith("Team"):
		string = string.split(" ")[1]
	
	if string[0] == "K":
		kRating = int(string[1:])
		if kRating < 75:
			hsRating = kRating
		if kRating < 100:
			hsRating = round(kRating + 10)
		elif kRating < 170:
			hsRating = round(110 + (kRating - 100) * 74/69)
		else:
			hsRating = round(185 + (kRating - 170) * 55/30)
		return (HillHeightClass(hsRating),hsRating)
	elif string[:2] == "HS":
		hsRating = int(string[2:])
		return (HillHeightClass(hsRating),hsRating)
	else:
		if string.startswith("Normal"):
			return ("NH",None)
		elif string.startswith("Large"):
			return ("LH",None)
		elif string.startswith("Flying"):
			return ("FH",None)
		raise Exception("Invalid hill!")



class Event:
	def __init__(self,eventId = None):
		if eventId != None:
			self.eventId = int(eventId)
			
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

			regex = re.findall(r'<div class="g-xs-24 justify-left"><div class="clip">[\w\n\s\.]+?</div>',html)
			tabKindsOfComps = list(map(ExtractContent,regex)) # dobimo tabelo oznak tekmovanj npr. 'HS240' ali 'Team HS140'
			tabKindsOfComps = [tabKindsOfComps[i].strip() for i in range(len(tabKindsOfComps)) if i % 2 == 0]

			tabHillHeights = list(map(HillCategory,tabKindsOfComps))

			tabOfGenderTags = re.findall('<div class="gender__item gender__item_\w">\w</div>',html)
			for genderTag in tabOfGenderTags:
				tabGenders.append(ExtractContent(genderTag))

			eventStatusItems = re.findall(r"<span class=\"status__item.+?>",html) # podatki o posameznem dogodku(ce je bil odpovedan, ce so rezultati na voljo)

			possibleCompetitions = []
			for i in range(len(urlsToComps)):
				results = True if re.search("Results available",eventStatusItems[4*i]) else False 
				cancelled = True if re.search("Cancelled",eventStatusItems[4*i + 3]) else False
				if results and not cancelled: # zagotovimo, da tekmovanje ni bilo odpovedano in da ima #
					if tabKindsOfComps[i].startswith('Team'): # je ekipna tekma
						possibleCompetitions.append(TeamCompetition(int(ExtractArgumentValueFromURL(urlsToComps[i],"raceid")),tabGenders[i],tabHillHeights[i]))
					else: # ni ekipna tekma
						possibleCompetitions.append(Competition(int(ExtractArgumentValueFromURL(urlsToComps[i],"raceid")),tabGenders[i],tabHillHeights[i]))
					time.sleep(.25) # nekaj casa pocakamo, da nas streznik ne blokira

			for i in range(len(possibleCompetitions)):
				if not possibleCompetitions[i].useless:
					self.competitions.append(possibleCompetitions[i])
		else:
			self.eventId = None
			self.location = None
			self.country = None
			self.competitions = []

		
class Competition:
	def __init__(self,raceId = None,gender = None,hillSize = None):
		if raceId != None:
			self.raceId = raceId
			self.gender = gender
			self.hillSizeName,self.hillSizeHeight = hillSize

			html = requests.get(f'https://www.fis-ski.com/DB/general/results.html?sectorcode=JP&raceid={raceId}').text
			tagCategory = re.search(r'<div class="event-header__subtitle">.+?</div>',html).group()
			self.category = ExtractContent(tagCategory)

			splitDocument = html.split('<div data-module="cells-join,list-false-links" class="table table_min_height">')
			if len(splitDocument) == 2:
				html = splitDocument[1]
				self.useless = False
			else:
				self.useless = True
			
			#podatki o rezultatih tekmovalcev
			# regex = re.findall(r'<div class="g-lg-1 g-md-1 g-sm-1 justify-right hidden-xs pr-1 gray">[0-9]+?</div>',html)
			# tabBib = list(map(ExtractContent,regex))
			if not self.useless:
				res = re.search(r"<span class=\"date__short\">[0-9\w\s\,]+?</span>",splitDocument[0])
				if res:
					self.date = Date.FromStr(ExtractContent(res.group()))
				else:
					self.date = None

				regex = re.findall(r'<div class="g-lg-2 g-md-2 g-sm-2 hidden-xs justify-right gray pr-1">[0-9]+?</div>',html)
				tabFisCode = list(map(ExtractContent,regex))

				regex = re.findall(r'<div class="g-lg g-md g-sm g-xs justify-left bold">[\-\w\n\s]+</div>',html)
				tabNames = list(map(ExtractContent,regex))
				tabNames = [name.strip() for name in tabNames] # odstranimo presledke

				regex = re.findall(r'<div class="g-lg-1 g-md-1 g-sm-2 g-xs-3 justify-left">[0-9\s]*?</div>',html)
				tabBirthYears = list(map(ExtractContent,regex))
				tabBirthYears = [birthYear.strip() for birthYear in tabBirthYears]

				regex = re.findall(r'<span class="country__name-short">.+?</span>',html)
				tabCountry = list(map(ExtractContent,regex))

				regex = re.findall(r'<div class="g-lg-2 g-md-2 g-sm-3 g-xs-5 justify-right blue bold ">[\-0-9\.\s]+</div>',html)
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

				# oznacmo kje je prvi veljavni rezultat
				start = 0
				for totalPoints in tabTotalPoints:
					if len(totalPoints) > 0:
						break
					start += 1
									
				if start == len(tabTotalPoints) or float(tabTotalPoints[start])	== 0.0:
					self.useless = True
				else:
					self.results = []
					for i in range(start,len(tabNames)):
						# ce so tocke tekmovalca zabelezene potem je rezultat veljaven, drugace pa je bil izkljucen, ali pa sploh ni skocil
						if len(tabTotalPoints[i]) > 0:
							name = ' '.join(tabNames[i].split()[1:])
							surname = tabNames[i].split()[0]
							birthYear = int(tabBirthYears[i]) if len(tabBirthYears[i]) > 0 else None 
							if hasPoints2:
								if len(tabPoints[2*i]) > 0 and len(tabPoints[2*i + 1]) > 0:
									self.results.append(Result(int(tabFisCode[i]),name,surname,birthYear,tabCountry[i],float(tabTotalPoints[i]),float(tabDistance[2*i]),float(tabPoints[2*i]),float(tabDistance[2*i + 1]),float(tabPoints[2*i + 1])))
								elif len(tabPoints[2*i]) > 0:
									self.results.append(Result(int(tabFisCode[i]),name,surname,birthYear,tabCountry[i],float(tabTotalPoints[i]),float(tabDistance[2*i]),float(tabPoints[2*i])))
								else:
									self.results.append(Result(int(tabFisCode[i]),name,surname,birthYear,tabCountry[i],float(tabTotalPoints[i])))
							elif hasPoints1:
								if len(tabPoints[i]) > 0:
									self.results.append(Result(int(tabFisCode[i]),name,surname,birthYear,tabCountry[i],float(tabTotalPoints[i]),float(tabDistance[i]),float(tabPoints[i])))
								else:
									self.results.append(Result(int(tabFisCode[i]),name,surname,birthYear,tabCountry[i],float(tabTotalPoints[i])))
							else:
								self.results.append(Result(int(tabFisCode[i]),name,surname,birthYear,tabCountry[i],float(tabTotalPoints[i])))
		
		else:
			self.raceId = None
			self.gender = None
			self.hillSizeName = None
			self.hillSizeHeight = None
			self.category = None
			self.date = None
			self.results = []

			
class Result:
	def __init__(self,fiscode,name,surname,birthYear,country,totalPoints,dist1 = None,points1 = None,dist2 = None,points2 = None):
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

	def __str__(self):
		ret = ""
		if self.points1 != None: 
			ret += f"\tSeries1: {self.distance1:.1f} m - {self.points1:.1f}\n"
		if self.points2 != None:
			ret += f"\tSeries2: {self.distance2:.1f} m - {self.points2:.1f}\n"
		ret += f"\tTotal points: {self.totalPoints:.1f}\n"
		return ret


class TeamCompetition:
	def __init__(self,raceId = None, gender = None,hillSize = None):
		if raceId != None:
			self.raceId = raceId
			self.gender = gender
			self.hillSizeName,self.hillSizeHeight = hillSize
			self.useless = False
			
			html = requests.get(f'https://www.fis-ski.com/DB/general/results.html?sectorcode=JP&raceid={raceId}').text
			tagCategory = re.search(r'<div class="event-header__subtitle">.+</div>',html).group()
			self.category = ExtractContent(tagCategory)

			splitDocument = html.split('<div data-module="cells-join,list-false-links" class="table table_min_height">')
			if len(splitDocument) == 2:
				html = splitDocument[1]
				self.useless = False
			else:
				self.useless = True
			
			if not self.useless:
				# datum
				res = re.search(r"<span class=\"date__short\">[0-9\w\s\,]+?</span>",splitDocument[0])
				if res:
					self.date = Date.FromStr(ExtractContent(res.group()))
				else:
					self.date = None

				#podatki o rezultatih ekip
				regex = re.findall(r'<div class="g-lg-9 g-md-9 g-sm-5 g-xs-11 justify-left bold">[\w\n\s\-]+</div>',html) 
				tabCountryAndNames = list(map(ExtractContent,regex)) #dobimo tako imena držav, kot vseh tekmovalcev
				tabCountryAndNames = [name.strip() for name in tabCountryAndNames]
				
				regex = re.findall(r'<div class="g-lg-2 g-md-2 g-sm-3 hidden-xs justify-right gray pr-1">[0-9]+?</div>',html)
				tabAllFisCodes = list(map(ExtractContent,regex)) #dobimo vse Fis kode, tudi od tekmovalcev
				
				regex = re.findall(r'<div class="g-lg-2 g-md-2 g-sm-3 g-xs-5 justify-right">[0-9.]+?</div>',html)
				tabTotalPoints = list(map(ExtractContent,regex))
				
				tabResultsOfCompetitors = []
				
				tabNames = []
				tabCountry = []
				country = None
				
				for i in range(len(tabCountryAndNames)): #ločimo imena držav in imena tekmovalcev, ter jim dodamo Fis kode in njihovo državo
					if tabCountryAndNames[i].isupper():#če je niz ves z velikimi črkami potem je država
						country = tabCountryAndNames[i]
						tabCountry.append([tabCountryAndNames[i],tabAllFisCodes[i]])
					else:
						tabNames.append([tabCountryAndNames[i],tabAllFisCodes[i],country])
				
				
				regex = re.findall(r'<div class="g-lg-1 g-md-1 g-sm-2 g-xs-3 justify-left">[0-9\s]*?</div>',html)
				tabBirthYears = list(map(ExtractContent,regex))
				tabBirthYears = [birthYears.strip() for birthYears in tabBirthYears]
				
				newHtml = html.split('<div class="g-lg-9 g-md-9 g-sm-5 g-xs-11 justify-left bold">')[1:]
				tabSoloResoults = [] #tabela tabel skokov/točk vsakega tekmovalca v ekipi
				for el in newHtml:
					if re.search(r'<span class="country__name-short">\w+?</span>',el) == None:#odstranimo države
						regex = re.findall(r'<div class="g-lg-2 g-md-2 g-sm-2 justify-right bold hidden-xs">[0-9\.]*?</div>',el)
						tabAllDistAndPoints = list(map(ExtractContent,regex))
						tabAllDistAndPoints = [el.strip() for el in tabAllDistAndPoints]
						tabSoloResoults.append(tabAllDistAndPoints)

				if len(tabSoloResoults) == 0:
					self.useless = True
				elif len(tabSoloResoults[0]) < 3 or (tabSoloResoults[0][0] == tabSoloResoults[0][2] and tabSoloResoults[0][3] == tabSoloResoults[0][1]): #bila je samo 1 serija
					for i in range(len(tabNames)):
						name = ' '.join(tabNames[i][0].split()[1:])
						surname = tabNames[i][0].split()[0]
						birthYear = int(tabBirthYears[i]) if len(tabBirthYears[i]) > 0 else None
						
						if tabSoloResoults[i] == []: #tekmovalec nima rezultata
							tabResultsOfCompetitors.append(Result(int(tabNames[i][1]),name,surname,birthYear,tabNames[i][2]))
						else:
							series1 = (float(tabSoloResoults[i][0]) if len(tabSoloResoults[i][0]) > 0 else None,float(tabSoloResoults[i][1]) if len(tabSoloResoults[i][1]) > 0 else None)
							tabResultsOfCompetitors.append(Result(int(tabNames[i][1]),name,surname,birthYear,tabNames[i][2],None,series1[0],series1[1]))
				else: # imamo 2 seriji
					for i in range(len(tabNames)):
						name = ' '.join(tabNames[i][0].split()[1:])
						surname = tabNames[i][0].split()[0]
						birthYear = int(tabBirthYears[i]) if len(tabBirthYears[i]) > 0 else None
			
						if tabSoloResoults[i] == []: #tekmovalec nima rezultata
							tabResultsOfCompetitors.append(Result(int(tabNames[i][1]),name,surname,birthYear,tabNames[i][2]))
						else:
							series1 = (float(tabSoloResoults[i][0]) if len(tabSoloResoults[i][0]) > 0 else None,float(tabSoloResoults[i][1]) if len(tabSoloResoults[i][1]) > 0 else None)
							series2 = (float(tabSoloResoults[i][2]) if len(tabSoloResoults[i][2]) > 0 else None,float(tabSoloResoults[i][3]) if len(tabSoloResoults[i][3]) > 0 else None) 
							tabResultsOfCompetitors.append(Result(int(tabNames[i][1]),name,surname,birthYear,tabNames[i][2],None,series1[0],series1[1],series2[0],series2[1]))
			
			if not self.useless:
				self.results = []
				namesPerTeam = int(len(tabNames)/len(tabCountry))#število članov v posamezni ekipi
				for i in range(len(tabCountry)):
					self.results.append(TeamResult(tabCountry[i][0],int(tabCountry[i][1]),float(tabTotalPoints[i]),tabResultsOfCompetitors[i*namesPerTeam:(i+1)*namesPerTeam]))
				
		else:
			self.raceId = None
			self.gender = None
			self.hillSizeName = None
			self.hillSizeHeight = None
			self.category = None
			self.date = None
			self.results = []

class TeamResult:#po posamezni državi
	def __init__(self,country = None,countryFisCode = None,totalPoints = None,tabResultsOfCompetitors = []):
		self.country = country
		self.countryFisCode = countryFisCode
		self.totalPoints = totalPoints
		self.results = c.deepcopy(tabResultsOfCompetitors)

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

	# koliko tekmovanj sledi
	thingsToWrite.append(s.pack("I",len(event.competitions)))
	for competition in event.competitions:
		if isinstance(competition,Competition):
			thingsToWrite.append(s.pack("?",True)) # povemo da je to navaden Competition, in ne TeamCompetition
			thingsToWrite.append(s.pack("I",competition.raceId))
			thingsToWrite.append(s.pack("c",bytes(competition.gender,encoding = "utf8")))
			thingsToWrite.extend(PackStrToBytes(competition.hillSizeName))
			if competition.hillSizeHeight == None:
				thingsToWrite.append(s.pack("I",0))
			else:
				thingsToWrite.append(s.pack("I",competition.hillSizeHeight))
			thingsToWrite.extend(PackStrToBytes(competition.category))
			thingsToWrite.append(competition.date.ToBytes())
			
			# koliko rezultatov sledi
			thingsToWrite.append(s.pack("I",len(competition.results)))
			for result in competition.results:
				thingsToWrite.append(s.pack("I",result.fisCode))
				thingsToWrite.extend(PackStrToBytes(result.name))
				thingsToWrite.extend(PackStrToBytes(result.surname))
				thingsToWrite.append(s.pack("I",result.birthYear if result.birthYear != None else 0))
				thingsToWrite.extend(PackStrToBytes(result.country))
				thingsToWrite.append(s.pack("f",result.totalPoints))

				# povemo ali ima rezultat tudi dolzino skoka in tocke prve in druge serije
				flagByte = 0
				if result.points1 != None:
					flagByte |= 1
				if result.points2 != None:
					flagByte |= 2
				thingsToWrite.append(s.pack("c",flagByte.to_bytes(1,byteorder = "little")))

				if flagByte & 1:
					thingsToWrite.append(s.pack("f",result.distance1))
					thingsToWrite.append(s.pack("f",result.points1))
				if flagByte & 2:
					thingsToWrite.append(s.pack("f",result.distance2))
					thingsToWrite.append(s.pack("f",result.points2))
		else: # TeamCompetition
			thingsToWrite.append(s.pack("?",False)) # povemo da je to TeamCompetition

			thingsToWrite.append(s.pack("I",competition.raceId))
			thingsToWrite.append(s.pack("c",bytes(competition.gender,encoding = "utf8")))
			thingsToWrite.extend(PackStrToBytes(competition.hillSizeName))
			if competition.hillSizeHeight == None:
				thingsToWrite.append(s.pack("I",0))
			else:
				thingsToWrite.append(s.pack("I",competition.hillSizeHeight))
			thingsToWrite.extend(PackStrToBytes(competition.category))
			thingsToWrite.append(competition.date.ToBytes())

			thingsToWrite.append(s.pack("I",len(competition.results)))
			for teamResult in competition.results:
				thingsToWrite.extend(PackStrToBytes(teamResult.country))
				thingsToWrite.append(s.pack("I",teamResult.countryFisCode))
				thingsToWrite.append(s.pack("f",teamResult.totalPoints))

				thingsToWrite.append(s.pack("I",len(teamResult.results)))
				for individualResult in teamResult.results:
					thingsToWrite.append(s.pack("I",individualResult.fisCode))
					thingsToWrite.extend(PackStrToBytes(individualResult.name))
					thingsToWrite.extend(PackStrToBytes(individualResult.surname))
					thingsToWrite.append(s.pack("I",individualResult.birthYear if individualResult.birthYear != None else 0))
					thingsToWrite.extend(PackStrToBytes(individualResult.country))

					# povemo ali ima rezultat tudi dolzino skoka in tocke prve in druge serije
					flagByte = 0
					if individualResult.points1 != None:
						flagByte |= 1
					if individualResult.points2 != None:
						flagByte |= 2
					thingsToWrite.append(s.pack("c",flagByte.to_bytes(1,byteorder = "little")))

					if flagByte & 1:
						thingsToWrite.append(s.pack("f",individualResult.distance1))
						thingsToWrite.append(s.pack("f",individualResult.points1))
					if flagByte & 2:
						thingsToWrite.append(s.pack("f",individualResult.distance2))
						thingsToWrite.append(s.pack("f",individualResult.points2))

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
			isNormalCompetition = s.unpack("?",data[offset:offset+1])[0]
			offset += 1
			if isNormalCompetition:
				competition = Competition()
				competition.raceId = s.unpack("I",data[offset:offset+4])[0]
				offset += 4
				competition.gender = s.unpack("c",data[offset:offset+1])[0].decode()
				offset += 1
				competition.hillSizeName,offset = UnpackStrFromBytes(data,offset)
				hillSizeHeight = s.unpack("I",data[offset:offset+4])[0]
				offset += 4
				if hillSizeHeight == 0:
					competition.hillSizeHeight = None
				else:
					competition.hillSizeHeight = hillSizeHeight
				competition.category,offset = UnpackStrFromBytes(data,offset)
				competition.date = Date.FromBytes(data[offset:offset+12])
				offset += 12

				# stevilo rezultatov pri posameznem tekmovanju
				numResults = s.unpack("I",data[offset:offset+4])[0]
				offset += 4
				for _ in range(numResults):
					fisCode = s.unpack("I",data[offset:offset+4])[0]
					offset += 4
					name,offset = UnpackStrFromBytes(data,offset)
					surname,offset = UnpackStrFromBytes(data,offset)
					birthYear = None if s.unpack("I",data[offset:offset+4])[0] == 0 else s.unpack("I",data[offset:offset+4])[0]
					offset += 4
					country,offset = UnpackStrFromBytes(data,offset)
					totalPoints = s.unpack("f",data[offset:offset+4])[0]
					offset += 4

					flagByte = int.from_bytes(s.unpack("c",data[offset:offset+1])[0],byteorder = "little")
					offset += 1

					distance1 = None
					points1 = None
					distance2 = None
					points2 = None
					if flagByte & 1:
						distance1 = s.unpack("f",data[offset:offset+4])[0]
						offset += 4
						points1 = s.unpack("f",data[offset:offset+4])[0]
						offset += 4
					if flagByte & 2:
						distance2 = s.unpack("f",data[offset:offset+4])[0]
						offset += 4
						points2 = s.unpack("f",data[offset:offset+4])[0]
						offset += 4

					competition.results.append(Result(fisCode,name,surname,birthYear,country,totalPoints,distance1,points1,distance2,points2))

				event.competitions.append(competition)
			else:
				teamCompetition = TeamCompetition()
				teamCompetition.raceId = s.unpack("I",data[offset:offset+4])[0]
				offset += 4
				teamCompetition.gender = s.unpack("c",data[offset:offset+1])[0].decode()
				offset += 1
				teamCompetition.hillSizeName,offset = UnpackStrFromBytes(data,offset)
				hillSizeHeight = s.unpack("I",data[offset:offset+4])[0]
				offset += 4
				if hillSizeHeight == 0:
					teamCompetition.hillSizeHeight = None
				else:
					teamCompetition.hillSizeHeight = hillSizeHeight
				teamCompetition.category,offset = UnpackStrFromBytes(data,offset)
				teamCompetition.date = Date.FromBytes(data[offset:offset+12])
				offset += 12

				numTeamResults = s.unpack("I",data[offset:offset+4])[0]
				offset += 4
				for _ in range(numTeamResults):
					teamResult = TeamResult()

					teamResult.country,offset = UnpackStrFromBytes(data,offset)
					teamResult.countryFisCode = s.unpack("I",data[offset:offset+4])[0]
					offset += 4
					teamResult.totalPoints = s.unpack("f",data[offset:offset+4])[0]
					offset += 4

					numIndividualResults = s.unpack("I",data[offset:offset+4])[0]
					offset += 4
					for _ in range(numIndividualResults):
						fisCode = s.unpack("I",data[offset:offset+4])[0]
						offset += 4
						name,offset = UnpackStrFromBytes(data,offset)
						surname,offset = UnpackStrFromBytes(data,offset)
						birthYear = None if s.unpack("I",data[offset:offset+4])[0] == 0 else s.unpack("I",data[offset:offset+4])[0]
						offset += 4
						country,offset = UnpackStrFromBytes(data,offset)

						flagByte = int.from_bytes(s.unpack("c",data[offset:offset+1])[0],byteorder = "little")
						offset += 1

						distance1 = None
						points1 = None
						distance2 = None
						points2 = None
						if flagByte & 1:
							distance1 = s.unpack("f",data[offset:offset+4])[0]
							offset += 4
							points1 = s.unpack("f",data[offset:offset+4])[0]
							offset += 4
						if flagByte & 2:
							distance2 = s.unpack("f",data[offset:offset+4])[0]
							offset += 4
							points2 = s.unpack("f",data[offset:offset+4])[0]
							offset += 4

						teamResult.results.append(Result(fisCode,name,surname,birthYear,country,None,distance1,points1,distance2,points2))

					teamCompetition.results.append(teamResult)

				event.competitions.append(teamCompetition)

		return event
	else:
		event = Event(eventId)
		# dogodek shranimo, da ob naslednjem zagonu programa ni treba spet dostopati do spletne strani
		WriteEventToFile(event)
		return event

def GetEventIds(start,end):
	''' Pridobi id stevilke dogodkov od leta start do leta end(vkljucno) in jih vrne kot seznam '''

	eventIds = []
	for year in range(start,end + 1):
		html = requests.get(f"https://www.fis-ski.com/DB/ski-jumping/calendar-results.html?eventselection=results&place=&sectorcode=JP&seasoncode={year}&categorycode=&disciplinecode=NH,LH,FH&gendercode=&racedate=&racecodex=&nationcode=&seasonmonth=X-{year}&saveselection=-1&seasonselection=").text

		tagsWithLinksToEvents = re.findall(r"<a class=\"pr-1 g-lg-1 g-md-1 g-sm-2 hidden-xs justify-left\"  href=\"http.+?\" target=\"_self\">",html)
		eventStatusItems = re.findall(r"<span class=\"status__item.+?>",html) # podatki o posameznem dogodku(ce je bil odpovedan, ce so rezultati na voljo)

		for i in range(len(tagsWithLinksToEvents)):
			results = True if re.search("Results available",eventStatusItems[4*i]) else False 
			cancelled = True if re.search("Cancelled",eventStatusItems[4*i + 3]) else False

			if results and not cancelled: # dogodek lahko obravnavamo le, ce ni bil odpovedan in so na voljo rezultati
				linkToEvent = ExtractURL(tagsWithLinksToEvents[i])
				eventId = ExtractArgumentValueFromURL(linkToEvent,"eventid")

				eventIds.append(eventId)

		time.sleep(.25) # nekaj casa pocakamo, da nas streznik ne blokira

	return list(map(int,eventIds))

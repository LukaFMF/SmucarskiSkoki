import re, os, struct as s

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
	lenght = len(string)
	return s.pack("I",lenght),s.pack(f"{length}s",string)

def ExtractURL(tag):
	''' Iz niza, ki vsebuje HTML znacko z URL naslovom izlusci ta URL '''
	return re.search(r"http.+?\"",tag).group()[:-1] # odstranimo zadnji znak, da se znebimo "


def WriteToFile(event):
	''' Zapise podani objekt razreda Event v binarno datoteko '''
	tingsToWrite = []

	# zapisemo lokacijo dogodka
	thingsToWrite.extend(PackStrToBytes(location))

	# signaliziramo ali sledi tudi datum, ki nam pove konec dogodka
	writeEndDate = event.endDate != None
	thingsToWrite.append(s.pack("?",writeEndDate))

	thingsToWrite.append(event.startDate.ToBytes())
	if writeEndDate:
		thingsToWrite.append(event.endDate.ToBytes())

	for competition in event.compettions:
		for result in competiton.results:
			pass

	dat = open(os.path.join("data",f"{event.id}.bin"),"wb")
	for dataInBytes in thingsToWrite:
		dat.write(dataInBytes)

	dat.close()

def ReadFromFile(eventId):
	if os.path.exists(os.path.join("data",f"{eventId}.bin")):
		pass
	else:
		pass

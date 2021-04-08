import tools as t

def athleteResults(events):
	athletes = []
	fisCodesToIndex = {}

	for i,event in enumerate(events):
		for j,competition in enumerate(event.competitions):
			if isinstance(competition,t.Competition):
				for k,result in enumerate(competition.results):
					if result.fisCode in fisCodesToIndex:
						inx = fisCodesToIndex[result.fisCode]
						athletes[inx].personalResults.append((i,j,k)) # k je indeks v tabeli rezutatov tekmovanja
					else:
						fisCodesToIndex[result.fisCode] = len(athletes)
						athletes.append(Athlete(result.fisCode,result.name,result.surname,result.birthYear,result.country,events))
						athletes[-1].personalResults.append((i,j,k)) # i je indeks v tabeli rezutatov tekmovanja

	return athletes,fisCodesToIndex

class Athlete:
	def __init__(self,fisCode,name,surname,birthYear,country,events):
		self.fisCode = fisCode
		self.name = name
		self.surname = surname
		self.birthYear = birthYear
		self.country = country
		self.personalResults = []
		self.events = events

	def __str__(self):
		ret = f"{self.fisCode}\n{self.name} {self.surname}\n{self.birthYear}\n{self.country}\n"
		for eventInx,compInx,placeInx in self.personalResults:
			ret += "\tPlace: " + str(placeInx + 1) + "\n"
			ret += str(self.events[eventInx].competitions[compInx].results[placeInx]) + "\n"

		return ret
import tools as t

def athleteResults(events):
	athletes = []
	fisCodesToIndex = {}

	for i,event in enumerate(events):
		for j,competition in enumerate(event.competitions):
			if isinstance(competition,t.Competition): # result at a solo competition is a 3-tuple
				for k,result in enumerate(competition.results):
					if result.fisCode in fisCodesToIndex:
						inx = fisCodesToIndex[result.fisCode]
						athletes[inx].personalResults.append((i,j,k)) # k je indeks v tabeli rezutatov tekmovanja
					else:
						fisCodesToIndex[result.fisCode] = len(athletes)
						athletes.append(Athlete(result.fisCode,result.name,result.surname,result.birthYear,result.country,events))
						athletes[-1].personalResults.append((i,j,k)) # i je indeks v tabeli rezutatov tekmovanja
			else: # result at a team competition is a 4-tuple
				for k,teamResult in enumerate(competition.results):
					for l,individualResult in enumerate(teamResult.results):
						if individualResult.fisCode in fisCodesToIndex:
							inx = fisCodesToIndex[individualResult.fisCode]
							athletes[inx].personalResults.append((i,j,k,l))
						else:
							fisCodesToIndex[individualResult.fisCode] = len(athletes)
							athletes.append(Athlete(individualResult.fisCode,individualResult.name,individualResult.surname,individualResult.birthYear,individualResult.country,events))
							athletes[-1].personalResults.append((i,j,k,l)) # i je indeks v tabeli rezutatov tekmovanja
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
		for res in self.personalResults:
			if len(res) == 3: # Solo tekma
				eventInx,compInx,placeInx = res
				ret += f"\tSOLO COMPETITION\n"
				ret += f"\tID: {self.events[eventInx].competitions[compInx].raceId}\n"
				ret += f"\tDate: {self.events[eventInx].competitions[compInx].date}\n"
				ret += f"\tRank: {t.ToOrdinalStr(placeInx + 1)} place\n"
				ret += f"{self.events[eventInx].competitions[compInx].results[placeInx]}\n"
			else:
				eventInx,compInx,teamPlaceInx,teamTabInx = res
				ret += f"\tTEAM COMPETITION\n"
				ret += f"\tID: {self.events[eventInx].competitions[compInx].raceId}\n"
				ret += f"\tDate: {self.events[eventInx].competitions[compInx].date}\n"
				ret += f"\tRank: {t.ToOrdinalStr(teamPlaceInx + 1)} place\n"
				ret += f"{self.events[eventInx].competitions[compInx].results[teamPlaceInx].results[teamTabInx]}\n"
		return ret
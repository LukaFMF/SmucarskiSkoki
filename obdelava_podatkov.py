import tools as t,ml
from datetime import *

def CompetitionsAtHomeVsForeign(athlete):
	events = athlete.events
	personalResults = athlete.personalResults

	# years = []
	# resultsAtHome = []
	# resultsElsewhere = []
	# for result in personalResults:
	# 	if len(result) == 3:
	# 		i,j,k = result
			
	# 		rank,competitionCountry,date = 
	# 		events[i].competitions[j].results[k]

	yearsAndAvgRelRankHome = {}
	yearsAndAvgRelRankAway = {}
	for result in personalResults:
		if len(result) == 3:
			i,j,k = result
			rank = k + 1
			numAllCompetitors = len(events[i].competitions[j].results)
			year = events[i].competitions[j].date.year
			if athlete.country == events[i].country:
				if year in yearsAndAvgRelRankHome:
					yearsAndAvgRelRankHome[year][0] += 1 - rank/numAllCompetitors
					yearsAndAvgRelRankHome[year][1] += 1
				else:
					yearsAndAvgRelRankHome[year] = [1 - rank/numAllCompetitors,1]
			else:
				if year in yearsAndAvgRelRankAway:
					yearsAndAvgRelRankAway[year][0] += 1 - rank/numAllCompetitors
					yearsAndAvgRelRankAway[year][1] += 1
				else:
					yearsAndAvgRelRankAway[year] = [1 - rank/numAllCompetitors,1]
				
	setOfYears = set(list(yearsAndAvgRelRankHome.keys()) + list(yearsAndAvgRelRankAway.keys()))

	for year in setOfYears:
		if year not in yearsAndAvgRelRankHome:
			yearsAndAvgRelRankHome[year] = [0.0,1]
		if year not in yearsAndAvgRelRankAway:
			yearsAndAvgRelRankAway[year] = [0.0,1]

	sortedYears = sorted(list(yearsAndAvgRelRankHome.keys()))

	averagesPerYearHome = []
	averagesPerYearAway = []
	for year in sortedYears:
		sumRelRanks,numRanks = yearsAndAvgRelRankHome[year]
		averagesPerYearHome.append(sumRelRanks/numRanks)

		sumRelRanks,numRanks = yearsAndAvgRelRankAway[year]
		averagesPerYearAway.append(sumRelRanks/numRanks)

	return sortedYears,(averagesPerYearHome,averagesPerYearAway)

	# results = []
	# for result in presonalResults:
	# 	if len(result) == 3:
	# 		i,j,k = result

	# 		rank = k + 1
	# 		allCompetitors = len(events[i].competitions[j].results)
	# 		date = events[i].competitions[j].date
	# 		timestamp = datetime(date.year,date.month,date.day).timestamp()

	# 		results.append((1 - rank/allCompetitors,timestamp))

	# results.sort(key = lambda x: x[1])

	# timestamps = [el[1] for el in results]
	values = [el[0] for el in results]

	return timestamps,values

excludedCategories = ("QUA","JUN","CHI","OPA","WJC","EYOF","YOG",'FC','UVS') # izlocimo kategorije, ki jih ne zelimo upostevati

def SimulateTeamCompetition(athletes,fisCodeMap,teamCountries,hillSizeName,hillSizeHeight,competitionCountry,startYear = 2020,endYear = 2021,gender = "M"):
	teams = []
	i = 0
	while i < len(teamCountries):
		team = TeamAthletesPrediction(athletes,teamCountries[i],hillSizeName,startYear,endYear,gender,False)
		if len(team) > 0:
			teams.append(team)
			i += 1
		else:
			print(f"Not enough results to form a team for {teamCountries[i]}. Disqualified!")
			teamCountries.remove(teamCountries[i])

	# pretvorimo fis kode v tetkmovalce
	for i in range(len(teams)):
		for j in range(len(teams[i])):
			teams[i][j] = athletes[fisCodeMap[teams[i][j]]]

	teamCompetition = t.TeamCompetition()
	teamCompetition.raceId = 0
	teamCompetition.gender = gender
	teamCompetition.hillSizeName = hillSizeName
	teamCompetition.hillSizeHeight = hillSizeHeight
	teamCompetition.date = t.Date(endYear,6,1)
	teamCompetition.category = "SIM"

	for i in range(len(teams)):
		teamResult = t.TeamResult()
		teamResult.country = teamCountries[i]
		teamResult.fisCode = None

		teamResult.totalPoints = 0.0
		for j in range(len(teams[i])):
			athlete = teams[i][j]

			points1 = ml.PredictNextJump(athlete,hillSizeHeight,competitionCountry,teamCompetition.date,1)
			points2 = ml.PredictNextJump(athlete,hillSizeHeight,competitionCountry,teamCompetition.date,2,points1)

			teamResult.totalPoints += points1 + points2
			
			teamResult.results.append(t.Result(athlete.fisCode,athlete.name,athlete.surname,athlete.birthYear,athlete.country,points1 + points2,None,points1,None,points2))

		teamCompetition.results.append(teamResult)

	teamCompetition.results.sort(key = lambda teamRes: teamRes.totalPoints,reverse = True)

	return teamCompetition


def TeamAthletesPrediction(athletes,country,hill = 'LH',startYear = 2020,endYear = 2021,gender = 'M',allowNoPointResults = True):
	''' Izpiše FIS kode najboljših 4-ih tekmovalcev glede na prej določen spol, ki imajo najboljšo uvrstitev na skakalnici te velikosti, v določenem intervalu let. '''
	fisCodeAndRes = {} #slovar ki ima ključe fisCode in vrednosti tabelo rankov
	for year in range(startYear,endYear + 1):
		for athlete in athletes:
			for result in athlete.personalResults:
				if len(result) == 3: # ne upostevamo ekipnih tekmovanj
					i,j,k = result
					if (athlete.country == country and
						athlete.events[i].competitions[j].gender == gender and
						athlete.events[i].competitions[j].hillSizeName == hill and
						athlete.events[i].competitions[j].hillSizeName == hill and
						# ce dovolimo rezultate brez tock preskocimo preverjanje points1 in points 2 
						(allowNoPointResults or (athlete.events[i].competitions[j].results[k].points1 != None and 
						athlete.events[i].competitions[j].results[k].points2 != None)) and
						athlete.events[i].competitions[j].date.year == year and
						athlete.events[i].competitions[j].category not in excludedCategories): # se ujema država
						if athlete.fisCode in fisCodeAndRes:
							fisCodeAndRes[athlete.fisCode].append(k+1)
						else:
							fisCodeAndRes[athlete.fisCode] = [k+1]

			

	fisCodes = list(fisCodeAndRes.keys())
	for fis in fisCodes:#naredimo povprečje rankov
		tabRes = fisCodeAndRes[fis]
		if len(tabRes) >= 5: # ima vsaj nekaj rezultatov
			average = sum(tabRes)/len(tabRes)
			fisCodeAndRes[fis] = average
		else:
			fisCodeAndRes.pop(fis)


	if len(fisCodeAndRes) < 4:
		return []

	final4tab = []
	brakpoint = sorted(list(fisCodeAndRes.values()))[3] #vzamemo 4. najboljši rezultat in z njim določimo tekmovace
	for fis,rez in fisCodeAndRes.items():
		if rez <= brakpoint:
			final4tab.append(fis)
		if len(final4tab) == 4:
			break
	return final4tab


def MostNRanks(athletes,n,startYear,endYear = None,gender = None):
	''' Vrne tabelo fis kod tekmovalcev, ki so najveckrat osvojili n-to mesto. Ce je ni vrne prazno tabelo '''
	if endYear == None:
		endYear = startYear

	if gender == None:
		gender = "MW"

	fisCodeAndNumN = dict()
	for year in range(startYear,endYear + 1):
		for athlete in athletes:
			for result in athlete.personalResults:
				if len(result) == 3: # ne upostevamo ekipnih tekmovanj
					i,j,k = result
					if (k + 1 == n and 
						athlete.events[i].competitions[j].gender in gender and 
						athlete.events[i].competitions[j].date.year == year and
						athlete.events[i].competitions[j].category not in excludedCategories): # ce je uvrstitev enaka iskani
						if athlete.fisCode in fisCodeAndNumN:
							fisCodeAndNumN[athlete.fisCode] += 1
						else:
							fisCodeAndNumN[athlete.fisCode] = 1

	mostNs = max(fisCodeAndNumN.values())

	tabMostNs = []
	for fisCode,numN in fisCodeAndNumN.items():
		if numN == mostNs:
			tabMostNs.append(fisCode)

	return tabMostNs,mostNs
	

def MostNRanksTeam(athletes,n,startYear,endYear = None,gender = None):
	if endYear == None:
		endYear = startYear

	if gender == None:
		gender = "MWA"

	fisCodeAndNumNOfATeam = dict()
	for year in range(startYear,endYear + 1):
		for athlete in athletes:
			for result in athlete.personalResults:
				if len(result) == 4: # upoštevamo le ekipne tekme
					i,j,k,l = result
					if (k + 1 == n and 
						athlete.events[i].competitions[j].gender in gender and 
						athlete.events[i].competitions[j].date.year == year and
						athlete.events[i].competitions[j].category not in excludedCategories):
						#athlete.events[i].competitions[j].results[k].results[l]
						if athlete.country in fisCodeAndNumNOfATeam:
							fisCodeAndNumNOfATeam[athlete.country] += 1
						else:
							fisCodeAndNumNOfATeam[athlete.country] = 1
	
	mostNs = max(fisCodeAndNumNOfATeam.values())
	
	tabMostNs = []
	
	for country,numN in fisCodeAndNumNOfATeam.items():
		if numN == mostNs:
			tabMostNs.append(country)
	return tabMostNs,mostNs







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
						athletes[-1].personalResults.append((i,j,k)) # k je indeks v tabeli rezutatov tekmovanja
			else: # result at a team competition is a 4-tuple
				for k,teamResult in enumerate(competition.results):
					for l,individualResult in enumerate(teamResult.results):
						if individualResult.fisCode in fisCodesToIndex:
							inx = fisCodesToIndex[individualResult.fisCode]
							athletes[inx].personalResults.append((i,j,k,l))
						else:
							fisCodesToIndex[individualResult.fisCode] = len(athletes)
							athletes.append(Athlete(individualResult.fisCode,individualResult.name,individualResult.surname,individualResult.birthYear,individualResult.country,events))
							athletes[-1].personalResults.append((i,j,k,l)) # k je indeks v tabeli rezutatov tekmovanja
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
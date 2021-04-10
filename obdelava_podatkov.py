import tools as t

def TeamAthletesPrediction(athletes,country,hill = 'LH',startYear = 2019,endYear = 2021,gender = 'M'):
    ''' Izpiše FIS kode najboljših 4-ih tekmovalcev glede na prej določen spol, ki imajo najboljšo uvrstitev na skakalnici te velikosti, v določenem intervalu let. '''
    fisCodeAndRes = {} #slovar ki ima ključe fisCode in vrednosti tabelo rankov
    for year in range(startYear,endYear + 1):
        for athlete in athletes:
            for result in athlete.personalResults:
                if len(result) == 3: # ne upostevamo ekipnih tekmovanj
                    i,j,k = result
                    if (athlete.events[i].competitions[j].date.year == year and
                        athlete.events[i].competitions[j].hillSizeName == hill and
                        athlete.events[i].competitions[j].gender == gender and
                        athlete.country == country): # se ujema država
                        if athlete.fisCode in fisCodeAndRes:
                            fisCodeAndRes[athlete.fisCode].append(k+1)
                        else:
                            fisCodeAndRes[athlete.fisCode] = [k+1]
    for fis in fisCodeAndRes.keys():#naredimo povprečje rankov
        tabRes = fisCodeAndRes[fis]
        average = sum(tabRes)/len(tabRes)
        fisCodeAndRes[fis] = average
    
    Final4tab = []
    brakpoint = sorted(list(fisCodeAndRes.values()))[3] #vzamemo 4. najboljši rezultat in z njim določimo tekmovace
    for fis,rez in fisCodeAndRes.items():
        if rez <= brakpoint:
            Final4tab.append((fis,rez))
    return Final4tab


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
                    if (athlete.events[i].competitions[j].date.year == year and
                        athlete.events[i].competitions[j].gender in gender and
                        k + 1 == n): # ce je uvrstitev enaka iskani
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
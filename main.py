import tools as t, time, datetime, obdelava_podatkov as op,charts,ml

eventIds = t.GetEventIds(2000,int(datetime.date.today().year))
# za popravit
eventIds.remove(13322) # cudne oblike
eventIds.remove(23918) # cudne oblike
eventIds.remove(24255) # cudne oblike
eventIds.remove(45432) # cudne oblike
eventIds.sort()
numEvents = len(eventIds)

start = time.time()
events = []
for i in range(numEvents):
    print(f"\rDownloading eventId {eventIds[i]} ({i+1}/{numEvents})",end = "")
    events.append(t.ReadEvent(eventIds[i]))

print(f"\n{(time.time() - start):.3f}s to load")

athletes,fisCodeMap = op.athleteResults(events)

rk = athletes[fisCodeMap[2918]]

pp = athletes[fisCodeMap[5658]]

# ryo = athletes[fisCodeMap[6288]]

# eisen = athletes[fisCodeMap[5253]]

# points1 = ml.PredictNextJump(eisen,240,"SLO",t.Date(2021,4,10),1)
# print(points1)
# points2 = ml.PredictNextJump(eisen,240,"SLO",t.Date(2021,4,10),2,points1)
# print(points2)

xAxis,yAxis = op.CompetitionsAtHomeVsForeign(rk)
charts.LineChart(xAxis,yAxis,"Relative rank of Robert Kranjec over his career","Time","Relative rank",["Home","Away"])

# teamComp = op.SimulateTeamCompetition(athletes,fisCodeMap,["SLO","GER","NOR","AUT","JPN","POL","RUS","SUI","FIN"],"LH",140,"SLO",2020,2050)

# for i in range(len(teamComp.results)):
# 	teamRes = teamComp.results[i]
# 	print(f"{(i + 1)}. {teamRes.country} - {teamRes.totalPoints:.1f}")
# 	for j in range(len(teamRes.results)):
# 		personalRes = teamRes.results[j]
# 		print(f"\t{personalRes.name} {personalRes.surname}: {personalRes.points1:.1f} - {personalRes.points2:.1f}")

# fisCodes = op.MostNRanks(athletes,1,2021,2021,"M")
# print(fisCodes)
# bigLoser = athletes[fisCodeMap[fisCodes[0][0]]]
# print(bigLoser.name,bigLoser.surname)
# fisCodes = op.TeamAthletesPrediction(athletes,'NOR',"LH",2021,2021)
# print(fisCodes)
# bigWinner1 = athletes[fisCodeMap[fisCodes[0][0]]]
# bigWinner2 = athletes[fisCodeMap[fisCodes[1][0]]]
# bigWinner3 = athletes[fisCodeMap[fisCodes[2][0]]]
# bigWinner4 = athletes[fisCodeMap[fisCodes[3][0]]]
# print(bigWinner1.name,bigWinner1.surname)
# print(bigWinner2.name,bigWinner2.surname)
# print(bigWinner3.name,bigWinner3.surname)
# print(bigWinner4.name,bigWinner4.surname)

# print("A")
# fisCodes = op.MostNRanks(athletes,1,2000,2021)
# print(fisCodes)
# bigWinner = athletes[fisCodeMap[fisCodes[0][0]]]
# print(bigWinner.name,bigWinner.surname)

# fisCodes = op.MostNRanks(athletes,2,2000,2021)
# print(fisCodes)
# bigWinner = athletes[fisCodeMap[fisCodes[0][0]]]
# print(bigWinner.name,bigWinner.surname)

# fisCodes = op.MostNRanks(athletes,3,2000,2021)
# print(fisCodes)
# bigWinner = athletes[fisCodeMap[fisCodes[0][0]]]
# print(bigWinner.name,bigWinner.surname)

# fisCodes = op.MostNRanks(athletes,4,2000,2021)
# print(fisCodes)
# bigLoser = athletes[fisCodeMap[fisCodes[0][0]]]
# print(bigLoser.name,bigLoser.surname)

# print("W")
# fisCodes = op.MostNRanks(athletes,1,2000,2021,"W")
# print(fisCodes)
# bigWinner = athletes[fisCodeMap[fisCodes[0][0]]]
# print(bigWinner.name,bigWinner.surname)

# fisCodes = op.MostNRanks(athletes,2,2000,2021,"W")
# print(fisCodes)
# bigWinner = athletes[fisCodeMap[fisCodes[0][0]]]
# print(bigWinner.name,bigWinner.surname)

# fisCodes = op.MostNRanks(athletes,3,2000,2021,"W")
# print(fisCodes)
# bigWinner = athletes[fisCodeMap[fisCodes[0][0]]]
# print(bigWinner.name,bigWinner.surname)

# fisCodes = op.MostNRanks(athletes,4,2000,2021,"W")
# print(fisCodes)
# bigLoser = athletes[fisCodeMap[fisCodes[0][0]]]
# print(bigLoser.name,bigLoser.surname)

# print("M")
# fisCodes = op.MostNRanks(athletes,1,2000,2021,"M")
# print(fisCodes)
# bigWinner = athletes[fisCodeMap[fisCodes[0][0]]]
# print(bigWinner.name,bigWinner.surname)

# fisCodes = op.MostNRanks(athletes,2,2000,2021,"M")
# print(fisCodes)
# bigWinner = athletes[fisCodeMap[fisCodes[0][0]]]
# print(bigWinner.name,bigWinner.surname)

# fisCodes = op.MostNRanks(athletes,3,2000,2021,"M")
# print(fisCodes)
# bigWinner = athletes[fisCodeMap[fisCodes[0][0]]]
# print(bigWinner.name,bigWinner.surname)

# fisCodes = op.MostNRanks(athletes,4,2000,2021,"M")
# print(fisCodes)
# bigLoser = athletes[fisCodeMap[fisCodes[0][0]]]
# print(bigLoser.name,bigLoser.surname)

#x = list(range(2000,2021 + 1))
# y = [[0,0,0,0,0] for _ in range(len(x))]

#for i in range(len(x)):
#    year = x[i]
#    for result in rk.personalResults:
#        if len(result) == 3 and rk.events[result[0]].competitions[result[1]].date.year == year:
#           rank = result[2] + 1
            
#           if 1 <= rank <= 3:
#               y[i][rank - 1] += 1
#           elif rank <= 10:
#               y[i][3] += 1
#           else:
#               y[i][4] += 1

# charts.BarChart(x,tuple(y),"Medals of Robert Kranjec","Year","Number of medals")
# for result in rk.personalResults:
#   if len(result) == 3 and rk.events[result[0]].competitions[result[1]].date.year == 2005 and result[2] == 0:
#       print(rk.events[result[0]].competitions[result[1]].raceId)
            
# izbran = athletes[fisCodeMap[6392]]
# tabTotalPoints = []
# for res in izbran.personalResults:
#   if len(res) == 3:
#       result = izbran.events[res[0]].competitions[res[1]].results[res[2]]
#       if result != None:
#           tabTotalPoints.append(result.totalPoints)
# print(tabTotalPoints)
# print(athletes[fisCodeMap[2918]])

#print(athletes[fisCodeMap[2918]])
#x = list(range(2000,2021 + 1))
#tabAverages = []
#y = []
#tabAverages2 = []
#y1 = []
#for i in range(len(x)):
#    year = x[i]
#    for result in rk.personalResults:
#        if (len(result) == 3 and rk.events[result[0]].competitions[result[1]].hillSizeName == 'LH' and
#        rk.events[result[0]].competitions[result[1]].results[result[2]].totalPoints != None
#        and rk.events[result[0]].competitions[result[1]].date.year == year):
#            y.append(rk.events[result[0]].competitions[result[1]].results[result[2]].totalPoints)
#    tabAverages.append(sum(y)/len(y) if len(y) != 0 else 0)
#    y = []
#    for result in pp.personalResults:
#        if (len(result) == 3 and pp.events[result[0]].competitions[result[1]].hillSizeName == 'LH' and
#        pp.events[result[0]].competitions[result[1]].results[result[2]].totalPoints != None
#        and pp.events[result[0]].competitions[result[1]].date.year == year):
#            y1.append(pp.events[result[0]].competitions[result[1]].results[result[2]].totalPoints)
#    tabAverages2.append(sum(y1)/len(y1) if len(y1) != 0 else 0)
#    y1 = []

#koncnatab = []
#koncnatab.append(tabAverages)
#koncnatab.append(tabAverages2)
#charts.LineChart(x,tuple(koncnatab),"Comparison of Robert Kranjec and Peter Prevc of total points in Flying hill","Year","Total points",['Robert','Peter'])


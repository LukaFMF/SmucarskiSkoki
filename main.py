import tools as t, time, datetime, obdelava_podatkov as op,charts,ml

eventIds = t.GetEventIds(2000,int(datetime.date.today().year))
# za popravit
eventIds.remove(11370) # cudne oblike
eventIds.remove(12302) # imena drzav z malimi crkami
eventIds.remove(13312) # cudne oblike
eventIds.remove(24925) # cudne oblike
eventIds.remove(26510) # imena drzav z malimi crkami
eventIds.remove(29577) # cudne oblike
eventIds.sort()
numEvents = len(eventIds)

start = time.time()
events = []
for i in range(numEvents):
    print(f"\rDownloading eventId {eventIds[i]} ({i+1}/{numEvents})",end = "")
    events.append(t.ReadEvent(eventIds[i]))

print(f"\n{(time.time() - start):.3f} s to load")

athletes,fisCodeMap = op.athleteResults(events)

rk = athletes[fisCodeMap[2918]]

pp = athletes[fisCodeMap[5658]]

# ml.PredictNextJump(rk)
    
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


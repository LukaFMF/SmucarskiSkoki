import tools as t, time, datetime, obdelava_podatkov as op

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


# athletes,fisCodeMap = op.athleteResults(events)

# print(athletes[fisCodeMap[6392]])

# Glavna stran
# leto = 2021
# html = requests.get(f"https://www.fis-ski.com/DB/ski-jumping/calendar-results.html?eventselection=results&place=&sectorcode=JP&seasoncode={leto}&categorycode=&disciplinecode=&gendercode=&racedate=&racecodex=&nationcode=&seasonmonth=X-{leto}&saveselection=-1&seasonselection=").text

# Eventi
# tagsOfEvents = re.findall(r"<a class=\"pr-1 g-lg-1 g-md-1 g-sm-2 hidden-xs justify-left\"  href=\".+?\" target=\"_self\">",html)
# urlsToEvents = list(map(t.ExtractURL,tagsOfEvents))
# print(urlsToEvents)



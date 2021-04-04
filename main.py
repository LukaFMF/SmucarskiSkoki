import tools as t

# event = t.ReadEvent(45208)
# print(event.location)
# print(event.competitions[2].results[40].distance1)

eventIds = t.GetEventIds(2000,2021)
events = []
for eventId in eventIds:
	print(eventId)
	events.append(t.ReadEvent(eventId))

# for eventId in eventIds:
# 	events.append(t.ReadEvent(eventId))

# Glavna stran
# leto = 2021
# html = requests.get(f"https://www.fis-ski.com/DB/ski-jumping/calendar-results.html?eventselection=results&place=&sectorcode=JP&seasoncode={leto}&categorycode=&disciplinecode=&gendercode=&racedate=&racecodex=&nationcode=&seasonmonth=X-{leto}&saveselection=-1&seasonselection=").text

# Eventi
# tagsOfEvents = re.findall(r"<a class=\"pr-1 g-lg-1 g-md-1 g-sm-2 hidden-xs justify-left\"  href=\".+?\" target=\"_self\">",html)
# urlsToEvents = list(map(t.ExtractURL,tagsOfEvents))
# print(urlsToEvents)

# = re.search(r"https:\/\/.*[0-9]{4}",found)




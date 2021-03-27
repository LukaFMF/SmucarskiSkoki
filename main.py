import re, requests, tools as t, time


class Event:
	pass
		
class Competition:
	pass

class Result:
	pass




class Athlete:
	pass


leto = 2021
html = requests.get(f"https://www.fis-ski.com/DB/ski-jumping/calendar-results.html?eventselection=results&place=&sectorcode=JP&seasoncode={leto}&categorycode=&disciplinecode=&gendercode=&racedate=&racecodex=&nationcode=&seasonmonth=X-{leto}&saveselection=-1&seasonselection=").text

tagsOfEvents = re.findall(r"<a class=\"pr-1 g-lg-1 g-md-1 g-sm-2 hidden-xs justify-left\"  href=\".+?\" target=\"_self\">",html)

urlsToEvents = list(map(t.ExtractURL,tagsOfEvents))
print(urlsToEvents)

time.sleep(.5)

# = re.search(r"https:\/\/.*[0-9]{4}",found)




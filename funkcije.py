import re, requests, tools as t, time
def getEventIDS(year = 2021):
    '''Za leto vrne tabelo ID-jev Eventov.'''
    tabEventIDS = []
    html = requests.get(f"https://www.fis-ski.com/DB/ski-jumping/calendar-results.html?eventselection=results&place=&sectorcode=JP&seasoncode={year}&categorycode=&disciplinecode=&gendercode=&racedate=&racecodex=&nationcode=&seasonmonth=X-{year}&saveselection=-1&seasonselection=").text
    tagsOfEvents = re.findall(r"<a class=\"pr-1 g-lg-1 g-md-1 g-sm-2 hidden-xs justify-left\"  href=\".+?\" target=\"_self\">",html)
    urlsToEvents = list(map(t.ExtractURL,tagsOfEvents))
    for Event in urlsToEvents:
        tabEventIDS.append(int(Event.split('eventid=')[1].split('&seasoncode')[0]))
    return tabEventIDS

def getCompetitionIDS(EventID):
    '''Vrne tabelo ID-jev Competitionov iz določenega ID-ja eventa. Prebere tudi spol tekmovalcev na tekmi.'''
    tabCompIDS = []
    tabGenders = []
    html = requests.get(f'https://www.fis-ski.com/DB/general/event-details.html?sectorcode=JP&eventid={EventID}').text
    tagsOfComps = re.findall(r'<a class="g-lg-1 g-md-1 g-sm-2 hidden-sm-down justify-left" href=".+" target="_self">',html)
    urlsToComps = list(map(t.ExtractURL,tagsOfComps))
    genders = re.findall('<div class="gender__item gender__item_\w">\w</div>',html)
    for g in genders:
        tabGenders.append(g.split('"')[-1][1])
    for Comp in urlsToComps:
        tabCompIDS.append(int(Comp.split('raceid=')[1]))
    return list(zip(tabGenders,tabCompIDS))
    
def getResoults(CompID):#preveri z re.search namesto re.findall
    html = requests.get(f'https://www.fis-ski.com/DB/general/results.html?sectorcode=JP&raceid={CompID}').text
    niz = re.findall(r'<h1 class="heading heading_l2 heading_white heading_off-sm-style">\D+</h1>',html)[0]
    niz = niz[:-1].split('>')[1].split('<')[0]#razbijemo na tabelo 2 el [city,country]
    city = niz.split()[0]
    country = niz.split()[1]
    category = re.findall(r'<div class="event-header__subtitle">.+</div>',html)[0]
    category = category[:-1].split('>')[-1].split('<')[0]
    tabRezultatov = [(category,city,country)]
    novHtml = html.split('<div class="g-lg g-md g-sm g-xs justify-left bold">')[1:]
    novHtml[-1] = novHtml[-1].split('<div class="g-corebine-embedded" style="height:auto"><footer class="m-footer" id="id-68950914"><div class="m-footer__wrap">')[0]
    for tekmovalec in novHtml:
        name = re.split('<div class="g-lg-1 g-md-1 g-sm-2 g-xs-3 justify-left">[1,2][0-9]{3}</div>',tekmovalec)[0]
        name = name.split('</div>')[0].split()#dobimo ime in priimek tekmovalca
        competitor = ''.join(el + ' ' for el in name)[:-1]
        resoults = re.findall('[0-9]{0,3}\.[0-9]',tekmovalec)#rezultati so oblike [dist1,points1,dist2,points2]
        resoults = [competitor] + list(map(float,resoults))
        tabRezultatov.append(resoults) #vrenmo tabelo imena + rezultatov 
    return tabRezultatov
import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
from tkinter import messagebox
import tools as t, time, datetime,obdelava_podatkov as op,charts
from math import sin,pi

def RadioInxToGender(inx):
	if inx == 0:
		return "M"
	elif inx == 1:
		return "F"
	return "A"

def RadioInxToHillRating(inx):
	if inx == 0:
		return "NH"
	elif inx == 1:
		return "LH"
	return "FH"

def IsHillHeightValid(hillSizeName,hillSizeHeight):
	if hillSizeName == "NH":
		return 85 <= hillSizeHeight <= 109
	elif hillSizeName == "LH":
		return 110 <= hillSizeHeight <= 184
	return hillSizeHeight >= 185 

class MainMenu(tk.Tk):
	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)
		self.title("Ski jumping analysis")
		self.geometry("400x300")
		self.resizable(False,True)
		
		self.events = []

		self.loadData = tk.Button(self,text='Load event data',command = self.LoadEvents)
		self.loadData.pack(fill="none", expand=True)

	def LoadEvents(self):
		self.loadData.destroy()

		startYear = 2000
		endYear = int(t.Date.Today().year)
		progress = tk.IntVar(self,0)
		barLen = 200
	
		yearInfoText = "Searching for events in year {}"
		loadingDescriptionText = tk.StringVar(self,yearInfoText.format(startYear))
		self.downloadInfo = tk.Label(self,textvariable = loadingDescriptionText)
		self.downloadInfo.pack(pady = (50,5))

		self.progressBar = ttk.Progressbar(self,orient = tk.HORIZONTAL,length = barLen,mode='determinate',variable = progress)
		self.progressBar.pack()
		self.update_idletasks()

		eventIds = []
		for year in range(startYear,endYear + 1):
			eventIds += t.GetEventIds(year,year)
			progress.set((year + 1 - startYear)/(endYear - startYear)*100)
			loadingDescriptionText.set(yearInfoText.format(min(year + 1,endYear)))
			self.update_idletasks()
			time.sleep(.01)

		eventIds.remove(13322) # cudne oblike
		eventIds.remove(23918) # cudne oblike
		eventIds.remove(24255) # cudne oblike
		eventIds.remove(45432) # cudne oblike
		eventIds.sort()
		numEvents = len(eventIds)

		progress.set(0)
		eventInfoText = "               Loading events: {}/" + str(numEvents) + "               " # ostaja vsebina prejsnje vsebine
		loadingDescriptionText.set(eventInfoText.format(0))
		self.update_idletasks()

		for i in range(numEvents):
			self.events.append(t.ReadEvent(eventIds[i]))
			progress.set((i+1)/numEvents*100)
			loadingDescriptionText.set(eventInfoText.format(min(i + 1,numEvents)))
			self.update_idletasks()

		self.athletes,self.fisCodeMap = op.athleteResults(self.events)

		self.downloadInfo.destroy()
		self.progressBar.destroy()

		self.InitMenu()

	def InitMenu(self):
		self.geometry("400x800")

		paddingY = (25,5) # top, bottom
		textsAndCommands = [
			("Simulate team competition:",self.Simulation),
			("Display athlete with most n-th places:",self.MostNthPlacesSolo),
			("Display country with most n-th places:",self.MostNthPlacesTeam),
			("Graph rank of a competition at home and away:",self.GraphHomeAway),
			("Display country\'s best team based on solo results:",self.TopTeamCountry),
			("Display all solo results of an athlete:",self.DisplaySoloResults),
			("Display all team results of a country:",self.DisplayTeamResults),
			("Graph number of medals for an athlete over the years:",self.GraphNumMedalsSolo),
			("Graph number of medals for a country over the years:",self.GraphNumMedalsTeam),
			("Compare average total scores of two athletes:",self.CompareTotalScores)
		]

		self.mainMenuLabelsAndButtons = []

		for text,command in textsAndCommands:
			label = tk.Label(text = text)
			button = tk.Button(self,text = "Open",command = command)
			label.pack(pady = paddingY)
			button.pack()
			self.mainMenuLabelsAndButtons.append((label,button))

	# def ShowTeamCompetition(self,master,teamComp):
	# 	sub = tk.Toplevel(master)
	# 	sub.wm_title("Simulation results")
	# 	sub.resizable(False,False)
	# 	#sub.geometry("400x400")

	# 	header = ("Rank","Country","Fis code","Name","Surname","Distance 1","Points 1","Distance 2","Points 2","Total points")

	# 	rows = [header]

	# 	for i,teamRes in enumerate(teamComp.results):
	# 		resultRow = []

	# 		rank = i + 1
	# 		resultRow.append(rank)
	# 		country = teamRes.country
	# 		resultRow.append(country)
	# 		totalPoints = teamRes.totalPoints

	# 		for result in teamRes.results:
	# 			fisCode = result.fisCode
	# 			resultRow.append(fisCode)

	# 			name = result.name
	# 			resultRow.append(name)

	# 			surname = result.surname
	# 			resultRow.append(surname)

	# 			distance1 = result.distance1
	# 			resultRow.append(distance1)

	# 			points1 = result.points1
	# 			resultRow.append(points1)

	# 			distance2 = result.distance2
	# 			resultRow.append(distance2)

	# 			points2 = result.points2
	# 			resultRow.append(points2)
			
	# 			resultRow.append(totalPoints)

	# 		for i in range(len(rows)):
	# 			for j in range(len(rows[0])):
	# 				self.soloResultEntry = tk.Entry(sub, width=20)
	# 				self.soloResultEntry.grid(row = i,column = j)
	# 				self.soloResultEntry.insert(tk.END,rows[i][j])

	
	def Simulation(self):
		self.simWindow = tk.Toplevel(self)
		self.simWindow.wm_title("Simulation")
		self.simWindow.resizable(False,False)
		self.simWindow.geometry("400x400")

		countries = sorted(['GER','AUT','JPN','FIN','NOR','POL','SLO','CZE','RUS','SUI'])

		self.simCountryListbox = tk.Listbox(self.simWindow,selectmode = "multiple")
		self.simCountryListbox.pack()
		for country in countries:
			self.simCountryListbox.insert(tk.END,country)

		self.simHillSizeName = tk.IntVar(self.simWindow,0)
		self.simHillSizeNameNHRadio = tk.Radiobutton(self.simWindow,text = "Normal hill",variable = self.simHillSizeName,value = 0) # 85–109
		self.simHillSizeNameLHRadio = tk.Radiobutton(self.simWindow,text = "Large hill",variable = self.simHillSizeName,value = 1) # 110–184
		self.simHillSizeNameFHRadio = tk.Radiobutton(self.simWindow,text = "Flying hill",variable = self.simHillSizeName,value = 2) # > 185
		self.simHillSizeNameNHRadio.pack()
		self.simHillSizeNameLHRadio.pack()
		self.simHillSizeNameFHRadio.pack()

		self.simHillSizeHeightSpin = tk.Spinbox(self.simWindow,state = "readonly",increment = 5,from_ = 85,to = 240)
		self.simHillSizeHeightSpin.pack()

		self.simCompetitionCountryCombobox = ttk.Combobox(self.simWindow,state="readonly",values = countries)
		self.simCompetitionCountryCombobox.pack()

		self.simGender = tk.IntVar(self.simWindow,0)
		self.simGenderMRadio = tk.Radiobutton(self.simWindow,text = "M",variable = self.simGender,value = 0)
		self.simGenderWRadio = tk.Radiobutton(self.simWindow,text = "W",variable = self.simGender,value = 1)
		self.simGenderMRadio.pack()
		self.simGenderWRadio.pack()

		currentYear = t.Date.Today().year
		self.simStartYearSpin = tk.Spinbox(self.simWindow,state = "readonly",from_ = 2000,to = currentYear)
		self.simEndYearSpin = tk.Spinbox(self.simWindow,state = "readonly",from_ = 2000,to = currentYear)
		self.simStartYearSpin.pack()
		self.simEndYearSpin.pack()


		self.execSimulationBtn = tk.Button(self.simWindow,text = 'Show results',command = self.SimulationExec)
		self.execSimulationBtn.pack()


	def SimulationExec(self):
		countries = sorted(['GER','AUT','JPN','FIN','NOR','POL','SLO','CZE','RUS','SUI'])
		selectedCountries = []
		for inx in self.simCountryListbox.curselection():
			selectedCountries.append(countries[inx])

		hillSizeName = RadioInxToHillRating(self.simHillSizeName)

		gender = RadioInxToGender(self.simGender.get())

		hillSizeHeight = int(self.simHillSizeHeightSpin.get())

		competitoionCountry = self.self.simCompetitionCountryCombobox.get()

		startYear = int(self.simStartYearSpin.get())
		endYear = int(self.simEndYearSpin.get())
		if IsHillHeightValid(hillSizeName,hillSizeHeight):
			if hillSizeName == "NH":
				tk.messagebox.showwarning('Warning','Selected for large hill, hill height must be between 85 and 109!')
			elif hillSizeName == "LH":
				tk.messagebox.showwarning('Warning','Selected for large hill, hill height must be between 110 and 184!')
			else:
				tk.messagebox.showwarning('Warning','Selected for flying hill, hill height must be 185 or above!')
		elif endYear < startYear:
			tk.messagebox.showwarning('Warning','Selected start year must be below selected end year!')
		elif len(selectedCountries) == 0:
			tk.messagebox.showwarning('Warning','You must select at least one competitor country!')
		else:
			teamCompetition = SimulateTeamCompetition(self.athletes,self.fisCodeMap,selectedCountries,hillSizeName,hillSizeHeight,competitionCountry,startYear,endYear,gender)
			self.ShowTeamCompetition(self.simWindow,teamCompetition)


	def MostNthPlacesSolo(self):
		self.simWindow = tk.Toplevel(self)
		sub.wm_title("Most solo n-th places")
		sub.resizable(False,False)
		sub.geometry("400x400")
    	#tk.Label(text = text)

		self.mostNPlabel = tk.Label(sub,text = 'Rank:')
		self.mostNPlabel.pack()
		self.mostNPlaceSpinbox = tk.Spinbox(sub, from_=1, to=50,state = 'readonly')
		self.mostNPlaceSpinbox.pack()
		
		self.mostNGender = tk.Label(sub,text = 'Gender:')
		self.mostNGender.pack()
		self.mostNGenderVar = tk.IntVar()
		self.mostNGenderMRadiobutton = tk.Radiobutton(sub, text="Male", variable=self.mostNGenderVar, value=0)
		self.mostNGenderMRadiobutton.pack()

		self.mostNGenderWRadiobutton = tk.Radiobutton(sub, text="Female", variable=self.mostNGenderVar, value=1) 
		self.mostNGenderWRadiobutton.pack()

		self.mostNloweryear = tk.Label(sub,text = 'From:')
		self.mostNloweryear.pack()
		currentYear = t.Date.Today().year
		self.mostNStartYearSpinbox = tk.Spinbox(sub, from_=2000, to=currentYear,state = 'readonly')
		self.mostNStartYearSpinbox.pack()

		self.mostNlupperyear = tk.Label(sub,text = 'To:')
		self.mostNlupperyear.pack()
		self.mostNEndYearSpinbox = tk.Spinbox(sub, from_= 2000, to=currentYear,state = 'readonly')
		self.mostNEndYearSpinbox.pack()


		self.execNPlaceBtn = tk.Button(sub,text = 'Show results',command = self.MostNthPlacesSoloExec)
		self.execNPlaceBtn.pack()

	def MostNthPlacesSoloExec(self):
		startYear = int(self.mostNStartYearSpinbox.get())
		endYear = int(self.mostNEndYearSpinbox.get())


		if endYear < startYear:
			tk.messagebox.showwarning('Warning','Selected start year must be below selected end year!')
			


	def MostNthPlacesTeam(self):
		sub = tk.Toplevel(self)
		sub.wm_title("Most team n-th places")
		sub.resizable(False,False)
		sub.geometry("400x400")

		self.mostNTeamPlacelabel = tk.Label(sub,text = 'Rank:')
		self.mostNTeamPlacelabel.pack()
		self.mostNTeamPlaceSpinbox = tk.Spinbox(sub, from_=1, to=50,state = 'readonly')
		self.mostNTeamPlaceSpinbox.pack()

		self.mostNTeamPlaceGenderlabel = tk.Label(sub,text = 'Gender:')
		self.mostNTeamPlaceGenderlabel.pack()
		self.mostNTeamGenderVar = tk.IntVar()
		self.mostNTeamGenderMRadiobutton = tk.Radiobutton(sub, text="Male", variable=self.mostNTeamGenderVar, value=0)
		self.mostNTeamGenderMRadiobutton.pack()

		self.mostNTeamGenderWRadiobutton = tk.Radiobutton(sub, text="Female", variable=self.mostNTeamGenderVar, value=1) 
		self.mostNTeamGenderWRadiobutton.pack()

		self.mostNTeamGenderARadiobutton = tk.Radiobutton(sub, text="Mixed", variable=self.mostNTeamGenderVar, value=2) 
		self.mostNTeamGenderARadiobutton.pack()

		currentYear = t.Date.Today().year

		self.mostNYearLowerlabel = tk.Label(sub,text = 'From:')
		self.mostNYearLowerlabel.pack()
		self.mostNTeamStartYearSpinbox = tk.Spinbox(sub, from_=2000, to= currentYear,state = 'readonly')
		self.mostNTeamStartYearSpinbox.pack()

		self.mostNYearUpperlabel = tk.Label(sub,text = 'To:')
		self.mostNYearUpperlabel.pack()
		self.mostNTeamEndYearSpinbox = tk.Spinbox(sub, from_= 2000, to= currentYear,state = 'readonly')
		self.mostNTeamEndYearSpinbox.pack()


		self.execNTeamPlaceBtn = tk.Button(sub,text = 'Show results',command = self.MostNthPlacesTeamExec)
		self.execNTeamPlaceBtn.pack()

	def MostNthPlacesTeamExec(self):
		startYear = int(self.mostNTeamStartYearSpinbox.get())
		endYear = int(self.mostNTeamEndYearSpinbox.get())

<<<<<<< HEAD

		if endYear < startYear:
			tk.messagebox.showwarning('Warning''Selected start year must be below selected end year!')
		
			

=======
>>>>>>> 1b55fbdf7a18da809846300cd6283e064fdcb541
	def GraphHomeAway(self):
		sub = tk.Toplevel(self)
		sub.wm_title("Home and away")
		sub.resizable(False,False)
		sub.geometry("400x400")

		self.Namelabel = tk.Label(sub,text = 'Name:')
		self.Namelabel.pack()
		self.awayNamebox = tk.Text(sub,height = 1,width = 25)
		self.Surnamelabel = tk.Label(sub,text = 'Surname:')
		self.Surnamelabel.pack()
		self.awaySurnamebox = tk.Text(sub,height = 1,width = 25)
		self.awayNamebox.pack()
		self.awaySurnamebox.pack()

		self.awayButtonExec = tk.Button(sub,text = "Show results",command = self.GraphHomeAwayExec)
		self.awayButtonExec.pack()


	def GraphHomeAwayExec(self):
		name = self.awayNamebox.get("1.0",tk.END).strip()
		surname = self.awaySurnamebox.get("1.0",tk.END).strip()
		fisCode = op.Athlete.GetAthleteFisByName(self.athletes,name,surname)

		if fisCode == None:
			tk.messagebox.showwarning("Warning",f"Name {name} {surname} not found!")
		else:
			athlete = self.athletes[self.fisCodeMap[fisCode]]
			xAxis,yAxis = op.CompetitionsAtHomeVsForeign(athlete)
			charts.LineChart(xAxis,yAxis,f"Relative rank of {athlete.name} {athlete.surname} over his career","Time","Relative rank",["Home","Away"])

	def ShowTopTeam(self,master,topTeam,country,hillSizeName):
		sub = tk.Toplevel(master)
		sub.wm_title(f"Top team for {country} on {hillSizeName}")
		sub.resizable(False,False)

		header = ("Fis code","Name","Surname","Birth year")

		rows = [header]

		for athlete in topTeam:
			resultRow = []

			resultRow.append(str(athlete.fisCode))
			resultRow.append(athlete.name) 
			resultRow.append(athlete.surname)

			birthYear = athlete.birthYear
			resultRow.append(str(birthYear) if birthYear != None else None)

			rows.append(tuple(resultRow))

		for i in range(len(rows)):
			for j in range(len(rows[0])):
				self.soloResultEntry = tk.Entry(sub, width=20)
				self.soloResultEntry.grid(row = i,column = j)
				self.soloResultEntry.insert(tk.END,rows[i][j])

	def TopTeamCountry(self):
		self.topTeamWindow = tk.Toplevel(self)
		self.topTeamWindow.wm_title("Top country team")
		self.topTeamWindow.resizable(False,False)
		self.topTeamWindow.geometry("400x400")

		#country,hill = 'LH',startYear = 2020,endYear = 2021,gender = 'M'

		countries = sorted(['GER','AUT','JPN','FIN','NOR','POL','SLO','CZE','RUS','SUI'])

		self.topTeamCountrylabel = tk.Label(sub,text = 'Country:')
		self.topTeamCountrylabel.pack()
		self.topTeamCountryCombobox= ttk.Combobox(self.topTeamWindow,values = countries,state = 'readonly')
		self.topTeamCountryCombobox.pack()
		
		self.topTeamHillSizelabel = tk.Label(sub,text = 'Hill sizes:')
		self.topTeamHillSizelabel.pack()

		self.topTeamHillSizeVar = tk.IntVar()
		self.topTeamHillSizeNH = tk.Radiobutton(self.topTeamWindow, text="Normal hill", variable=self.topTeamHillSizeVar, value=0)
		self.topTeamHillSizeNH.pack() 
		self.topTeamHillSizeLH = tk.Radiobutton(self.topTeamWindow, text="Large hill", variable=self.topTeamHillSizeVar, value=1)
		self.topTeamHillSizeLH.pack()
		self.topTeamHillSizeFH = tk.Radiobutton(self.topTeamWindow, text="Flying hill", variable=self.topTeamHillSizeVar, value=2)
		self.topTeamHillSizeFH.pack()

		self.topGenderlabel = tk.Label(sub,text = 'Gender:')
		self.topGenderlabel.pack()
		self.topTeamGenderVar = tk.IntVar()
		self.topTeamGenderMRadiobutton = tk.Radiobutton(self.topTeamWindow, text="Male", variable=self.topTeamGenderVar, value=0)
		self.topTeamGenderMRadiobutton.pack()

		self.topTeamGenderWRadiobutton = tk.Radiobutton(self.topTeamWindow, text="Female", variable=self.topTeamGenderVar, value=1) 
		self.topTeamGenderWRadiobutton.pack()

		self.topTeamGenderARadiobutton = tk.Radiobutton(self.topTeamWindow, text="Mixed", variable=self.topTeamGenderVar, value=2) 
		self.topTeamGenderARadiobutton.pack()

		self.loweryearlabel = tk.Label(sub,text = 'From:')
		self.loweryearlabel.pack()
		currentYear = t.Date.Today().year
		self.topTeamStartYearSpinbox = tk.Spinbox(self.topTeamWindow, from_=2000, to=currentYear,state = 'readonly')
		self.topTeamStartYearSpinbox.pack()

		self.upperyearlabel = tk.Label(sub,text = 'To:')
		self.upperyearlabel.pack()
		self.topTeamEndYearSpinbox = tk.Spinbox(self.topTeamWindow, from_= 2000, to=currentYear,state = 'readonly')
		self.topTeamEndYearSpinbox.pack()


		self.exectopTeamCountryBtn = tk.Button(self.topTeamWindow,text = 'Show results',command = self.TopTeamCountryExec)
		self.exectopTeamCountryBtn.pack()

	def TopTeamCountryExec(self):
		country = self.topTeamCountryCombobox.get()
		gender =  RadioInxToGender(self.topTeamGenderVar.get())

		hillSizeName = RadioInxToHillRating(self.topTeamHillSizeVar.get())

		startYear = int(self.topTeamStartYearSpinbox.get())
		endYear = int(self.topTeamEndYearSpinbox.get())

		if endYear < startYear: #popravimo meje
			tk.messagebox.showwarning(title='Warning', message='Selected start year must be below selected end year!', **options)
		else:
			tabFisCodes = op.TeamAthletesPrediction(self.athletes,country,hillSizeName,startYear,endYear,gender)
			if len(tabFisCodes) < 4:
				tk.messagebox.showwarning(title='Warning', message='There is not enough competitors to foram a team!', **options)
			else:
				tabAthletes = []
				for i in range(len(tabFisCodes)):
					tabAthletes.append(self.athletes[self.fisCodeMap[tabFisCodes[i]]])

				self.ShowTopTeam(self.topTeamWindow,tabAthletes,country,hillSizeName)

	def ShowSoloResults(self,master,athlete,soloResults):
		sub = tk.Toplevel(master)
		sub.wm_title(f"Solo results for {athlete.name} {athlete.surname}")
		sub.resizable(False,False)
		#sub.geometry("400x400")


		header = ("Rank","Distance 1","Points 1","Distance 2","Points 2","Total points","Hill rating","Hill size","Location","Date")

		rows = [header]

		for result in soloResults:
			i,j,k = result
			resultRow = []

			resultRow.append(str(k + 1)) # Rank

			event = self.events[i]
			competition = self.events[i].competitions[j]
			personalResult = self.events[i].competitions[j].results[k]

			distance1 = personalResult.distance1
			resultRow.append(f"{distance1:.1f}" if distance1 != None else "")

			points1 = personalResult.points1
			resultRow.append(f"{points1:.1f}" if points1 != None else "")

			distance2 = personalResult.distance2
			resultRow.append(f"{distance2:.1f}" if distance2 != None else "")

			points2 = personalResult.points2
			resultRow.append(f"{points2:.1f}" if points2 != None else "")

			totalPoints = f"{personalResult.totalPoints:.1f}"
			resultRow.append(totalPoints)

			hillSizeName = competition.hillSizeName
			resultRow.append(hillSizeName)

			hillSizeHeight = str(competition.hillSizeHeight)
			resultRow.append(str(hillSizeHeight) if hillSizeHeight != None else "")

			location = event.country
			resultRow.append(location)

			date = competition.date
			resultRow.append(str(date))

			rows.append(tuple(resultRow))

		for i in range(len(rows)):
			for j in range(len(rows[0])):
				self.soloResultEntry = tk.Entry(sub, width=20)
				self.soloResultEntry.grid(row = i,column = j)
				self.soloResultEntry.insert(tk.END,rows[i][j])

	def DisplaySoloResults(self):
		self.displaySoloResultsWindow = tk.Toplevel(self)
		self.displaySoloResultsWindow.wm_title("Solo results")
		self.displaySoloResultsWindow.resizable(False,False)
		self.displaySoloResultsWindow.geometry("400x400")

		self.soloResultsNamelabel = tk.Label(self.displaySoloResultsWindow,text = 'Name:')
		self.soloResultsNamelabel.pack()
		self.soloResultsNamebox = tk.Text(self.displaySoloResultsWindow,height = 1,width = 25)
		self.soloResultsSurnamelabel = tk.Label(self.displaySoloResultsWindow,text = 'Surname:')
		self.soloResultsSurnamelabel.pack()
		self.soloResultsSurnamebox = tk.Text(self.displaySoloResultsWindow,height = 1,width = 25)
		self.soloResultsNamebox.pack()
		self.soloResultsSurnamebox.pack()

		self.soloResultsStartYearLowerlabel = tk.Label(self.displaySoloResultsWindow,text = 'From:')
		self.soloResultsStartYearLowerlabel.pack()
		currentYear = t.Date.Today().year
		self.soloResultsStartYearSpin = tk.Spinbox(self.displaySoloResultsWindow, from_= 2000, to= currentYear,state = 'readonly')
		self.soloResultsStartYearupperlabel = tk.Label(self.displaySoloResultsWindow,text = 'To:')
		self.soloResultsStartYearupperlabel.pack()
		self.soloResultsEndYearSpin = tk.Spinbox(self.displaySoloResultsWindow, from_= 2000, to= currentYear,state = 'readonly')
		self.soloResultsStartYearSpin.pack()
		self.soloResultsEndYearSpin.pack()

		self.soloResultsButtonExec = tk.Button(self.displaySoloResultsWindow,text = "Show results",command = self.DisplaySoloResultsExec)
		self.soloResultsButtonExec.pack()

	def DisplaySoloResultsExec(self):
		name = self.soloResultsNamebox.get("1.0",tk.END).strip()
		surname = self.soloResultsSurnamebox.get("1.0",tk.END).strip()
		fisCode = op.Athlete.GetAthleteFisByName(self.athletes,name,surname)

		startYear = int(self.soloResultsStartYearSpin.get())
		endYear = int(self.soloResultsEndYearSpin.get())

		if fisCode == None:
			tk.messagebox.showwarning("Warning",f"Name {name} {surname} not found!")
		elif endYear < startYear:
			tk.messagebox.showwarning("Warning","Selected start year must be below selected end year.")
		else:
			athlete = self.athletes[self.fisCodeMap[fisCode]]

			soloResults = []
			for perseonalResult in athlete.personalResults:
				if len(perseonalResult) == 3:
					i,j,k = perseonalResult
					if startYear <= athlete.events[i].competitions[j].date.year <= endYear:
						soloResults.append(perseonalResult)

			self.ShowSoloResults(self.displaySoloResultsWindow,athlete,soloResults)


	def DisplayTeamResults(self):
		sub = tk.Toplevel(self)
		sub.wm_title("Team results")
		sub.resizable(False,False)
		sub.geometry("400x400")

		countries = sorted(['GER','AUT','JPN','FIN','NOR','POL','SLO','CZE','RUS','SUI'])

		self.displayTeamResultsCountrieslabel = tk.Label(sub,text = 'Country')
		self.displayTeamResultsCountrieslabel.pack()
		self.displayTeamResultsCountriesCombobox= ttk.Combobox(sub,values = countries,state = 'readonly')
		self.displayTeamResultsCountriesCombobox.pack()

		self.lowerYearlabel = tk.Label(sub,text = 'From')
		self.lowerYearlabel.pack()
		self.displayTeamResultsStartYearSpinbox = tk.Spinbox(sub, from_=2000, to=2021,state = 'readonly')
		self.displayTeamResultsStartYearSpinbox.pack()

		self.upperYearlabel = tk.Label(sub,text = 'To')
		self.upperYearlabel.pack()
		self.displayTeamResultsEndtYearSpinbox = tk.Spinbox(sub, from_= 2000, to=2021,state = 'readonly')
		self.displayTeamResultsEndtYearSpinbox.pack()


		self.execdisplayTeamResultBtn = tk.Button(sub,text = 'Show results',command = self.DisplayTeamResultsExec)
		self.execdisplayTeamResultBtn.pack()

	def DisplayTeamResultsExec(self):
		if int(self.displayTeamResultsEndtYearSpinbox.get()) < int(self.displayTeamResultsEndtYearSpinbox.get()):
			tk.messagebox.showwarning(title='Warning', message='Selected start year must be below selected end year.')
		else:
			tabTeamResults = []
			start = int(self.displayTeamResultsStartYearSpinbox.get())
			end = int(self.displayTeamResultsEndtYearSpinbox.get())
			country = self.displayTeamResultsCountriesCombobox.get()
			for athlete in self.athletes:
				if athlete.country == country:
					for result in athlete.personalResults:
						if len(result) == 4:	
							i,j,k,l = result
							if start <= athlete.events[i].competitions[j].date.year <= end:
								tabTeamResults.append(result)
							
			

	def GraphNumMedalsSolo(self):
		sub = tk.Toplevel(self)
		sub.wm_title("Solo results")
		sub.resizable(False,False)
		sub.geometry("400x400")

		self.numMedalsSoloNamelabel = tk.Label(sub,text = 'Name')
		self.numMedalsSoloNamelabel.pack()
		self.numMedalsSoloNamebox = tk.Text(sub,height = 1,width = 25)
		self.numMedalsSoloSurnamelabel = tk.Label(sub,text = 'Surname')
		self.numMedalsSoloSurnamelabel.pack()
		self.numMedalsSoloSurnamebox = tk.Text(sub,height = 1,width = 25)
		self.numMedalsSoloNamebox.pack()
		self.numMedalsSoloSurnamebox.pack()

		self.numMedalsSoloButtonExec = tk.Button(sub,text = "Show results",command = self.GraphNumMedalsSoloExec)
		self.numMedalsSoloButtonExec.pack()
	
	def GraphNumMedalsSoloExec(self):
		name = self.numMedalsSoloNamebox.get("1.0",tk.END).strip()
		surname = self.numMedalsSoloSurnamebox.get("1.0",tk.END).strip()
		fisCode = op.Athlete.GetAthleteFisByName(self.athletes,name,surname)

		if fisCode == None:
			tk.messagebox.showwarning("Warning",f"Name {name} {surname} not found!")
		else:
			athlete = self.athletes[self.fisCodeMap[fisCode]]
			yearsCompeted = set()
			for result in athlete.personalResults:
				if len(result) == 3:
					i,j,k = result
					yearsCompeted.add(athlete.events[i].competitions[j].date.year)


			minYear = min(yearsCompeted)
			maxYear = max(yearsCompeted)

			xAxis = list(range(minYear,maxYear + 1))
			yAxis = [[0,0,0] for _ in range(len(xAxis))]
			for i in range(len(xAxis)):
				year = xAxis[i]
				for result in athlete.personalResults:
					if len(result) == 3:
						if athlete.events[result[0]].competitions[result[1]].date.year == year:
							rank = result[2] + 1
							
							if 1 <= rank <= 3:
								yAxis[i][rank - 1] += 1

			charts.BarChart(xAxis,tuple(yAxis),f"Medals of {athlete.name} {athlete.surname} in their career","Year","Number of medals",["Gold","Silver","Bronze"],["gold","silver","#CD7F32"])
		

	def GraphNumMedalsTeam(self):
		sub = tk.Toplevel(self)
		sub.wm_title("Team medals")
		sub.resizable(False,False)
		sub.geometry("400x400")

		countries = sorted(['GER','AUT','JPN','FIN','NOR','POL','SLO','CZE','RUS','SUI'])
		
		self.graphNUmberTeamsCountrylabel = tk.Label(sub,text = 'Country')
		self.graphNUmberTeamsCountrylabel.pack()
		self.graphNUmberTeamsCountryCombobox= ttk.Combobox(sub,values = countries,state = 'readonly')
		self.graphNUmberTeamsCountryCombobox.pack()

		self.execgraphNUmberTeamsCountryBtn = tk.Button(sub,text = 'Show results',command = self.GraphNumMedalsTeamExec)
		self.execgraphNUmberTeamsCountryBtn.pack()

	def GraphNumMedalsTeamExec(self):
		allYears = set()
		country = self.graphNUmberTeamsCountryCombobox.get()
		tabTeamResults = []
		for athlete in self.athletes:
			if athlete.country == country:
				for result in athlete.personalResults:
					if len(result) == 4:	
						i,j,k,l = result
						tabTeamResults.append(result)
						allYears.add(athlete.events[i].competitions[j].date.year)
		lower = min(allYears)
		upper = max(allYears)
		x = list(range(lower,upper + 1))
		y = [[0,0,0] for _ in range(len(x))]
		for index in range(len(x)):
			year = x[index] 
			for res in tabTeamResults:
				i,j,k,l = res
				if self.events[i].competitions[j].date.year == year:
					rank = k + 1
					if 1 <= rank <= 3:
						y[index][rank - 1] += 1
		charts.BarChart(x,tuple(list(y)),f'Chart presenting the number of medals of {country}','Years','Medals',['Gold','SIlver','Bronze'],['gold','silver','#cd7f32'])
					

	def CompareTotalScores(self):
		sub = tk.Toplevel(self)
		sub.wm_title("Comparison")
		sub.resizable(False,False)
		sub.geometry("400x400")

		self.CompareTotalScoresName1label = tk.Label(sub,text = 'Name:')
		self.CompareTotalScoresName1label.pack()
		self.CompareTotalScoresNamebox1 = tk.Text(sub,height = 1,width = 25)
		self.CompareTotalScoresSurname1label = tk.Label(sub,text = 'Surname:')
		self.CompareTotalScoresSurnamebox1 = tk.Text(sub,height = 1,width = 25)
		self.CompareTotalScoresNamebox1.pack()
		self.CompareTotalScoresSurnamebox1.pack()

		self.CompareTotalScoresName2label = tk.Label(sub,text = 'Name:')
		self.CompareTotalScoresName2label.pack()
		self.CompareTotalScoresNamebox2 = tk.Text(sub,height = 1,width = 25)
		self.CompareTotalScoresSurname2label = tk.Label(sub,text = 'Surname:')
		self.CompareTotalScoresSurname2label.pack()
		self.CompareTotalScoresSurnamebox2 = tk.Text(sub,height = 1,width = 25)
		self.CompareTotalScoresNamebox2.pack()
		self.CompareTotalScoresSurnamebox2.pack()

		self.CompareTotalScoresHillSizelabel = tk.Label(sub,text = 'Hill size:')
		self.CompareTotalScoresHillSizelabel.pack()
		self.CompareTotalScoresHillSizeNameVar = tk.IntVar(sub,0)
		self.CompareTotalScoresHillSize1Radio = tk.Radiobutton(sub,text = "Normal hill",variable = self.CompareTotalScoresHillSizeNameVar,value = 0) # 85–109
		self.CompareTotalScoresHillSize2Radio = tk.Radiobutton(sub,text = "Large hill",variable = self.CompareTotalScoresHillSizeNameVar,value = 1) # 110–184
		self.CompareTotalScoresHillSize3Radio = tk.Radiobutton(sub,text = "Flying hill",variable = self.CompareTotalScoresHillSizeNameVar,value = 2) # > 185
		self.CompareTotalScoresHillSize3Radio.pack()
		self.CompareTotalScoresHillSize2Radio.pack()
		self.CompareTotalScoresHillSize1Radio.pack()


		self.execCompareTotalScoresBtn = tk.Button(sub,text = 'Show results',command = self.CompareTotalScoresExec)
		self.execCompareTotalScoresBtn.pack()

	def CompareTotalScoresExec(self):
		HillSizeVar = self.CompareTotalScoresHillSizeNameVar.get()
		HillSizeName = ['NH','LH','FH'][HillSizeVar]

		name1 = self.CompareTotalScoresNamebox1.get("1.0",tk.END).strip()
		surname1 = self.CompareTotalScoresSurnamebox1.get("1.0",tk.END).strip()
		fisCode1 = op.Athlete.GetAthleteFisByName(self.athletes,name1,surname1)

		name2 = self.CompareTotalScoresNamebox2.get("1.0",tk.END).strip()
		surname2 = self.CompareTotalScoresSurnamebox2.get("1.0",tk.END).strip()
		fisCode2 = op.Athlete.GetAthleteFisByName(self.athletes,name2,surname2)

		if fisCode1 == None:  
			tk.messagebox.showwarning("Warning",f"Name {name1} {surname1} not found!")
		if fisCode2 == None:
			tk.messagebox.showwarning("Warning",f"Name {name2} {surname2} not found!")
		else:
			athlete1 = self.athletes[self.fisCodeMap[fisCode1]]
			tabAverageTotalPoints1 = []
			y1 = []

			athlete2 = self.athletes[self.fisCodeMap[fisCode2]]
			tabAverageTotalPoints2 = []
			y2 = []

			setBothYears = set()
			for result1 in athlete1.personalResults:
					if len(result1) == 3 and athlete1.events[result1[0]].competitions[result1[1]].hillSizeName == HillSizeName:
						i,j,k = result1
						setBothYears.add(athlete1.events[i].competitions[j].date.year)
			for result2 in athlete2.personalResults:
					if len(result2) == 3 and athlete2.events[result2[0]].competitions[result2[1]].hillSizeName == HillSizeName:
						i,j,k = result2
						setBothYears.add(athlete2.events[i].competitions[j].date.year)
			lower = min(setBothYears)
			upper = max(setBothYears)
			x = list(range(lower,upper))
			print(x)
			for i in range(len(x)):
				year = x[i]
				for result1 in athlete1.personalResults:
					if (len(result1) == 3 and athlete1.events[result1[0]].competitions[result1[1]].hillSizeName == HillSizeName
					and athlete1.events[result1[0]].competitions[result1[1]].date.year == year):
						y1.append(athlete1.events[result1[0]].competitions[result1[1]].results[result1[2]].totalPoints)
				tabAverageTotalPoints1.append(sum(y1)/len(y1) if len(y1) != 0 else 0) #če ni total pointov dodamo v tabelo povprečij 0
				y1 = []

			for i in range(len(x)):
				year = x[i]
				for result2 in athlete2.personalResults:
					if (len(result2) == 3 and athlete2.events[result2[0]].competitions[result2[1]].hillSizeName == HillSizeName and
					athlete2.events[result2[0]].competitions[result2[1]].results[result2[2]].totalPoints != None
					and athlete2.events[result2[0]].competitions[result2[1]].date.year == year):
						y2.append(athlete2.events[result2[0]].competitions[result2[1]].results[result2[2]].totalPoints)
				tabAverageTotalPoints2.append(sum(y2)/len(y2) if len(y2) != 0 else 0)
				y2 = []
			print(tabAverageTotalPoints1)
			print(tabAverageTotalPoints2)


			charts.LineChart(x,(tabAverageTotalPoints1,tabAverageTotalPoints2),f'Comparison between {athlete1.name} {athlete2.surname} and {athlete2.name} {athlete2.surname}','Year','Average total points',[athlete2.surname,athlete2.surname])




# window = Tk()
# var = StringVar()
# var.set("one")
# data=("one", "two", "three", "four")
# cb=Combobox(window, values=data)
# cb.place(x=60, y=150)

# lb=Listbox(window, height=5, selectmode='multiple')
# for num in data:
#     lb.insert(END,num)
# lb.place(x=250, y=150)

# v0=IntVar()
# r1=Radiobutton(window, text="male", variable=v0,value=1)
# r2=Radiobutton(window, text="female", variable=v0,value=2)
# v0.set(1)
# r1.place(x=100,y=50)
# r2.place(x=180, y=50)

				
# v1 = IntVar()
# v2 = IntVar()
# C1 = Checkbutton(window, text = "Cricket", variable = v1)
# C2 = Checkbutton(window, text = "Tennis", variable = v2)
# C1.place(x=100, y=100)
# C2.place(x=180, y=100)

# window.title('Hello Python')
# window.geometry("400x400+20+20")
# window.mainloop()
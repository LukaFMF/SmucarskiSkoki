import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
from tkinter import messagebox
import tools as t, time, datetime,obdelava_podatkov as op,charts
from math import sin,pi


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

		# self.simLabel = tk.Label(text = "Simulate team competition:")
		# self.simBtn = tk.Button(self,text = "Open",command = self.Simulation)
		# self.simLabel.pack(pady = paddingY)
		# self.simBtn.pack()

		# self.mostNRanksSoloLabel = tk.Label(text = "Display athlete with most n-th places:")
		# self.mostNRanksSoloBtn = tk.Button(self,text='Open',command = self.MostNthPlacesSolo)
		# self.mostNRanksSoloLabel.pack(pady = paddingY)
		# self.mostNRanksSoloBtn.pack()

		# self.mostNRanksTeamLabel = tk.Label(self,text = "Display country with most n-th places")
		# self.mostNRanksTeamBtn = tk.Button(self,text="Open",command = self.MostNthPlacesTeam)
		# self.mostNRanksTeamLabel.pack(pady = paddingY)
		# self.mostNRanksTeamBtn.pack()

		# self.homeAndAwayLabel = tk.Label(self,text = "Graph rank of a competition at home and away")
		# self.homeAndAwayBtn = tk.Button(self,text = "Open",command = self.GraphHomeAway)
		# self.homeAndAwayLabel.pack(pady = paddingY)
		# self.homeAndAwayBtn.pack()

		# self.topTeamInCountryLabel = tk.Label(self,text = "Display country\'s best team based on solo results")
		# self.topTeamInCountryBtn = tk.Button(self,text = "Open",command = self.TopTeamCountry)
		# self.topTeamInCountryLabel.pack(pady = paddingY)
		# self.topTeamInCountryBtn.pack()

		# self.allSoloResultsBtn = tk.Button(self,text='Display all solo results of an athlete',command = self.DisplaySoloResults)

		# self.allTeamResultsBtn = tk.Button(self,text='Display all team results of a country',command = self.DisplayTeamResults)

		# self.podiumBarChartSoloBtn = tk.Button(self,text='Graph number of medals for an athlete over the years',command = self.GraphNumMedalsSolo)

		# self.podiumBarChartTeamBtn = tk.Button(self,text='Graph number of medals for a country over the years',command = self.GraphNumMedalsTeam)

		# self.compareAthletesBtn = tk.Button(self,text='Compare average total scores of two athletes',command = self.CompareTotalScores)

		
	def Simulation(self):
		sub = tk.Toplevel(self)
		sub.wm_title("Simulation")
		sub.resizable(False,False)
		sub.geometry("400x400")

		countries = sorted(['GER','AUT','JPN','FIN','NOR','POL','SLO','CZE','RUS','SUI'])

		self.simCountryListbox = tk.Listbox(sub,selectmode = "multiple")
		self.simCountryListbox.pack()
		for country in countries:
			self.simCountryListbox.insert(tk.END,country)

		self.simHillSizeName = tk.IntVar(sub,0)
		self.simHillSizeNameNHRadio = tk.Radiobutton(sub,text = "Normal hill",variable = self.simHillSizeName,value = 0) # 85–109
		self.simHillSizeNameLHRadio = tk.Radiobutton(sub,text = "Large hill",variable = self.simHillSizeName,value = 1) # 110–184
		self.simHillSizeNameFHRadio = tk.Radiobutton(sub,text = "Flying hill",variable = self.simHillSizeName,value = 2) # > 185
		self.simHillSizeNameNHRadio.pack()
		self.simHillSizeNameLHRadio.pack()
		self.simHillSizeNameFHRadio.pack()

		self.simHillSizeHeightSpin = tk.Spinbox(sub,state = "readonly",increment = 5,from_ = 85,to = 240)
		self.simHillSizeHeightSpin.pack()

		self.simCompetitionCountryCombobox = ttk.Combobox(sub,state="readonly",values = countries)
		self.simCompetitionCountryCombobox.pack()

		self.simGender = tk.IntVar(sub,0)
		self.simGenderMRadio = tk.Radiobutton(sub,text = "M",variable = self.simGender,value = 0)
		self.simGenderWRadio = tk.Radiobutton(sub,text = "W",variable = self.simGender,value = 1)
		self.simGenderMRadio.pack()
		self.simGenderWRadio.pack()

		currentYear = t.Date.Today().year
		self.simStartYearSpin = tk.Spinbox(sub,state = "readonly",from_ = 2000,to = currentYear)
		self.simEndYearSpin = tk.Spinbox(sub,state = "readonly",from_ = 2000,to = currentYear)
		self.simStartYearSpin.pack()
		self.simEndYearSpin.pack()


		self.execSimulationBtn = tk.Button(sub,text = 'Show results',command = self.SimulationExec)
		self.execSimulationBtn.pack()

		#teamCountries,hillSizeName,hillSizeHeight,competitionCountry,startYear = 2020,endYear = 2021,gender = "M"

	def SimulationExec(self):
		print(self.simCountryListbox.curselection())
		print(self.simCompetitionCountry.get())
		print(int(self.simHillSizeHeightSpin .get()))
		print(int(self.simStartYearSpin.get()))
		print(int(self.simEndYearSpin.get()))

	def MostNthPlacesSolo(self):
		sub = tk.Toplevel(self)
		sub.wm_title("Most solo n-th places")
		sub.resizable(False,False)
		sub.geometry("400x400")

		self.mostNPlaceSpinbox = tk.Spinbox(sub, from_=1, to=50,state = 'readonly')
		self.mostNPlaceSpinbox.pack()

		self.mostNGenderVar = tk.IntVar()
		self.mostNGenderMRadiobutton = tk.Radiobutton(sub, text="Male", variable=self.mostNGenderVar, value=0)
		self.mostNGenderMRadiobutton.pack()

		self.mostNGenderWRadiobutton = tk.Radiobutton(sub, text="Female", variable=self.mostNGenderVar, value=1) 
		self.mostNGenderWRadiobutton.pack()

		currentYear = t.Date.Today().year
		self.mostNStartYearSpinbox = tk.Spinbox(sub, from_=2000, to=currentYear,state = 'readonly')
		self.mostNStartYearSpinbox.pack()

		
		self.mostNEndYearSpinbox = tk.Spinbox(sub, from_= 2000, to=currentYear,state = 'readonly')
		self.mostNEndYearSpinbox.pack()


		self.execNPlaceBtn = tk.Button(sub,text = 'Show results',command = self.MostNthPlacesSoloExec)
		self.execNPlaceBtn.pack()

	def MostNthPlacesSoloExec(self):
		

		if int(self.mostNEndYearSpinbox.get()) < int(self.mostNStartYearSpinbox.get()): #popravimo meje
			tk.messagebox.showwarning(title='Warning', message='Selected start year must be below selected end year.')
			


	def MostNthPlacesTeam(self):
		sub = tk.Toplevel(self)
		sub.wm_title("Most team n-th places")
		sub.resizable(False,False)
		sub.geometry("400x400")

		self.mostNTeamPlaceSpinbox = tk.Spinbox(sub, from_=1, to=50,state = 'readonly')
		self.mostNTeamPlaceSpinbox.pack()

		self.mostNTeamGenderVar = tk.IntVar()
		self.mostNTeamGenderMRadiobutton = tk.Radiobutton(sub, text="Male", variable=self.mostNTeamGenderVar, value=0)
		self.mostNTeamGenderMRadiobutton.pack()

		self.mostNTeamGenderWRadiobutton = tk.Radiobutton(sub, text="Female", variable=self.mostNTeamGenderVar, value=1) 
		self.mostNTeamGenderWRadiobutton.pack()

		self.mostNTeamGenderARadiobutton = tk.Radiobutton(sub, text="Mixed", variable=self.mostNTeamGenderVar, value=2) 
		self.mostNTeamGenderARadiobutton.pack()

		currentYear = t.Date.Today().year

		self.mostNTeamStartYearSpinbox = tk.Spinbox(sub, from_=2000, to= currentYear,state = 'readonly')
		self.mostNTeamStartYearSpinbox.pack()

		
		self.mostNTeamEndYearSpinbox = tk.Spinbox(sub, from_= 2000, to= currentYear,state = 'readonly')
		self.mostNTeamEndYearSpinbox.pack()


		self.execNTeamPlaceBtn = tk.Button(sub,text = 'Show results',command = self.MostNthPlacesTeamExec)
		self.execNTeamPlaceBtn.pack()

	def MostNthPlacesTeamExec(self):
		
		
		
		if int(self.mostNTeamEndYearSpinbox.get()) < int(self.mostNTeamStartYearSpinbox.get()): 
			tk.messagebox.showwarning(title='Warning', message='Selected start year must be below selected end year.', **options)
			

	def GraphHomeAway(self):
		sub = tk.Toplevel(self)
		sub.wm_title("Home and away")
		sub.resizable(False,False)
		sub.geometry("400x400")

		self.awayNamebox = tk.Text(sub,height = 1,width = 25)
		self.awaySurnamebox = tk.Text(sub,height = 1,width = 25)
		self.awayNamebox.pack()
		self.awaySurnamebox.pack()

		self.awayButtonExec = tk.Button(sub,text = "Show results",command = self.GraphHomeAwayExec)
		self.awayButtonExec.pack()


	def GraphHomeAwayExec(self):
		name = self.awayNamebox.get("1.0",tk.END).strip()
		surname = self.awaySurnamebox.get("1.0",tk.END).strip()
		fisCode = op.Athlete.GetAthleteFisByName(self.athletes,self.name,surname)

		if fisCode == None:
			tk.messagebox.showwarning("Warning",f"Name {name} {surname} not found!")
		else:
			athlete = self.athletes[self.fisCodeMap[fisCode]]
			xAxis,yAxis = op.CompetitionsAtHomeVsForeign(athlete)
			charts.LineChart(xAxis,yAxis,f"Relative rank of {athlete.name} {athlete.surname} over his career","Time","Relative rank",["Home","Away"])


	def TopTeamCountry(self):
		sub = tk.Toplevel(self)
		sub.wm_title("Top country team")
		sub.resizable(False,False)
		sub.geometry("400x400")

		#country,hill = 'LH',startYear = 2020,endYear = 2021,gender = 'M'

		countries = sorted(['GER','AUT','JPN','FIN','NOR','POL','SLO','CZE','RUS','SUI'])

		
		self.topTeamCountryCombobox= ttk.Combobox(sub,values = countries,state = 'readonly')
		self.topTeamCountryCombobox.pack()
		
		self.topTeamHillSizeVar = tk.IntVar()
		self.topTeamHillSizeNH = tk.Radiobutton(sub, text="Normal hill", variable=self.topTeamHillSizeVar, value=0)
		self.topTeamHillSizeNH.pack() 
		self.topTeamHillSizeLH = tk.Radiobutton(sub, text="Large hill", variable=self.topTeamHillSizeVar, value=1)
		self.topTeamHillSizeLH.pack()
		self.topTeamHillSizeFH = tk.Radiobutton(sub, text="Flying hill", variable=self.topTeamHillSizeVar, value=2)
		self.topTeamHillSizeFH.pack()

		self.topTeamGenderVar = tk.IntVar()
		self.topTeamGenderMRadiobutton = tk.Radiobutton(sub, text="Male", variable=self.topTeamGenderVar, value=0)
		self.topTeamGenderMRadiobutton.pack()

		self.topTeamGenderWRadiobutton = tk.Radiobutton(sub, text="Female", variable=self.topTeamGenderVar, value=1) 
		self.topTeamGenderWRadiobutton.pack()

		self.topTeamGenderARadiobutton = tk.Radiobutton(sub, text="Mixed", variable=self.topTeamGenderVar, value=2) 
		self.topTeamGenderARadiobutton.pack()

		currentYear = t.Date.Today().year
		self.topTeamStartYearSpinbox = tk.Spinbox(sub, from_=2000, to=currentYear,state = 'readonly')
		self.topTeamStartYearSpinbox.pack()

		
		self.topTeamEndYearSpinbox = tk.Spinbox(sub, from_= 2000, to=currentYear,state = 'readonly')
		self.topTeamEndYearSpinbox.pack()


		self.exectopTeamCountryBtn = tk.Button(sub,text = 'Show results',command = self.TopTeamCountryExec)
		self.exectopTeamCountryBtn.pack()

	def TopTeamCountryExec(self):



		if int(self.topTeamEndYearSpinbox.get()) < int(self.topTeamStartYearSpinbox.get()): #popravimo meje
			tk.messagebox.showwarning(title='Warning', message='Selected start year must be below selected end year.', **options)

	def DisplaySoloResults(self):
		sub = tk.Toplevel(self)
		sub.wm_title("Solo results")
		sub.resizable(False,False)
		sub.geometry("400x400")

		self.soloResultsNamebox = tk.Text(sub,height = 1,width = 25)
		self.soloResultsSurnamebox = tk.Text(sub,height = 1,width = 25)
		self.soloResultsNamebox.pack()
		self.soloResultsSurnamebox.pack()

		currentYear = t.Date.Today().year
		self.soloResultsStartYearSpin = tk.Spinbox(sub, from_= 2000, to= currentYear,state = 'readonly')
		self.soloResultsEndYearSpin = tk.Spinbox(sub, from_= 2000, to= currentYear,state = 'readonly')
		self.soloResultsStartYearSpin.pack()
		self.soloResultsEndYearSpin.pack()

		self.soloResultsButtonExec = tk.Button(sub,text = "Show results",command = self.DisplaySoloResultsExec)

	def DisplaySoloResultsExec(self):
		name = self.soloResultsNamebox.get("1.0",tk.END).strip()
		surname = self.soloResultsSurnamebox.get("1.0",tk.END).strip()
		fisCode = op.Athlete.GetAthleteFisByName(self.athletes,name,surname)

		startYear = int(self.soloResultsStartYearSpin)
		endYear = int(self.soloResultsEndYearSpin)

		if fisCode == None:
			tk.messagebox.showwarning("Warning",f"Name {name} {surname} not found!")
		elif endYear < startYear:
			tk.messagebox.showwarning("Warning","Selected start year must be below selected end year.")
		else:
			athlete = athletes[fisCodeMap[fisCode]]

			soloResults = []
			for perseonalResult in athlete.personalResults:
				if len(perseonalResult) == 3:
					soloResults.append(perseonalResult)

			# todo


	def DisplayTeamResults(self):
		sub = tk.Toplevel(self)
		sub.wm_title("Team results")
		sub.resizable(False,False)
		sub.geometry("400x400")

		countries = sorted(['GER','AUT','JPN','FIN','NOR','POL','SLO','CZE','RUS','SUI'])

		
		self.displayTeamResultsCountriesCombobox= ttk.Combobox(sub,values = countries,state = 'readonly')
		self.displayTeamResultsCountriesCombobox.pack()


		self.displayTeamResultsStartYearSpinbox = tk.Spinbox(sub, from_=2000, to=2021,state = 'readonly')
		self.displayTeamResultsStartYearSpinbox.pack()

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

		self.numMedalsSoloNamebox = tk.Text(sub,height = 1,width = 25)
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
		pass

	def newWind(self):
		t = tk.Toplevel(self)
		t.wm_title("Window 1")
		t.geometry("600x500")




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
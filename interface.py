import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
import tools as t, time, datetime,obdelava_podatkov as op
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

		self.ahtletes,self.fisCodeMap = op.athleteResults(self.events)

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

		self.simHillSizeName = tk.IntVar(0)
		self.simHillSizeNameNHRadio




		self.execSimulationBtn = tk.Button(sub,text = 'Show results',command = self.Simulate)
		self.execSimulationBtn.pack()

		#teamCountries,hillSizeName,hillSizeHeight,competitionCountry,startYear = 2020,endYear = 2021,gender = "M"

	def Simulate(self):
		pass


		

		

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


		self.mostNStartYearSpinbox = tk.Spinbox(sub, from_=2000, to=2021,state = 'readonly')
		self.mostNStartYearSpinbox.pack()

		
		self.mostNEndYearSpinbox = tk.Spinbox(sub, from_= 2000, to=2021,state = 'readonly')
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


		self.mostNTeamStartYearSpinbox = tk.Spinbox(sub, from_=2000, to=2021,state = 'readonly')
		self.mostNTeamStartYearSpinbox.pack()

		
		self.mostNTeamEndYearSpinbox = tk.Spinbox(sub, from_= 2000, to=2021,state = 'readonly')
		self.mostNTeamEndYearSpinbox.pack()


		self.execNTeamPlaceBtn = tk.Button(sub,text = 'Show results',command = self.MostNthPlacesTeamExec)
		self.execNTeamPlaceBtn.pack()

	def MostNthPlacesTeamExec(self):
		
		
		
		if int(self.mostNTeamEndYearSpinbox.get()) < int(self.mostNTeamStartYearSpinbox.get()): 
			tk.messagebox.showwarning(title='Warning', message='Selected start year must be below selected end year.', **options)
			

	def GraphHomeAway(self):
		pass

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


		self.topTeamStartYearSpinbox = tk.Spinbox(sub, from_=2000, to=2021,state = 'readonly')
		self.topTeamStartYearSpinbox.pack()

		
		self.topTeamEndYearSpinbox = tk.Spinbox(sub, from_= 2000, to=2021,state = 'readonly')
		self.topTeamEndYearSpinbox.pack()


		self.exectopTeamCountryBtn = tk.Button(sub,text = 'Show results',command = self.TopTeamCountryExec)
		self.exectopTeamCountryBtn.pack()

	def TopTeamCountryExec(self):




		if int(self.topTeamEndYearSpinbox.get()) < int(self.topTeamStartYearSpinbox.get()): #popravimo meje
			tk.messagebox.showwarning(title='Warning', message='Selected start year must be below selected end year.', **options)

	def DisplaySoloResults(self):
		pass


	def DisplaySoloResultsExec(self):
		pass

	def DisplayTeamResults(self):
		pass

	def DisplayTeamResultsExec(self):
		pass

	def GraphNumMedalsSolo(self):
		pass

	def GraphNumMedalsTeam(self):
		pass

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
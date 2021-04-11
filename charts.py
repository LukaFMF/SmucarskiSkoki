import matplotlib.pyplot as plt,random as r

class ChartException(Exception):
	def __init__(self,msg):
		super().__init__(msg)

def BarChart(xAxis,yAxis,title = None,xLabel = None,yLabel = None,tabLabels = None,tabColors = None):
	''' x: [2001, 2002, ... ], y: ([3,3,...],[3,6,..],[54,64,..],[34,54,...]) '''
	width = 0.15

	if title != None:
		if not isinstance(title,str):
			raise ChartException("Chart title must be a string!")
		plt.title(title)

	if xLabel != None:
		if not isinstance(xLabel,str):
			raise ChartException("Label on x axis must be a string!")
		plt.xlabel(xLabel)

	if yLabel != None:
		if not isinstance(yLabel,str):
			raise ChartException("Label on y axis must be a string!")
		plt.ylabel(yLabel)
	plt.xticks(xAxis,map(str,xAxis))

	tabOffsets = [[] for _ in range(len(xAxis))]
	for i,xValue in enumerate(xAxis):
		interval = None
		if len(yAxis[0]) % 2 == 0 or (len(yAxis[0]) // 2) % 2 == 1:
			interval = len(yAxis[0]) // 2 + 1
		else:
			interval = len(yAxis[0]) // 2 + 2

		for mul in range(-interval,interval + 1,2):
			tabOffsets[i].append(xValue + mul*0.5*width)
	
	colors = None
	defaultColors = ["#3498EB","#9C3094","#E2E629","#3F5DE0","#F8271F"]
	if tabColors != None:
		if len(tabColors) != len(yAxis[0]):
			raise ChartException("Number of colors must match the number of data sets!")
		colors = tabColors
	else:
		colorsNeeded = len(yAxis[0])
		if colorsNeeded > len(defaultColors):
			colorsToGenerate = colorsNeeded - len(defaultColors)
			generatedColors = []
			for _ in range(colorsToGenerate):
				generatedColors.append("#" + "".join(map(str,r.sample("0123456789ABCDEF",6))))

			colors = defaultColors + generatedColors
		else:
			colors = defaultColors[:colorsNeeded]

	labels = None
	if tabLabels != None:
		if len(tabLabels) != len(yAxis[0]):
			raise ChartException("Number of labels must match the number of data sets!")
		labels = tabLabels
	else:
		labelsNeeded = len(yAxis[0])
		labels = [str(i) for i in range(1,labelsNeeded + 1)]

	for i in range(len(xAxis)):
		for j in range(len(yAxis[0])):
			if i == 0:
				plt.bar(tabOffsets[i][j],yAxis[i][j],width,color = colors[j],label = labels[j])
			else:
				plt.bar(tabOffsets[i][j],yAxis[i][j],width,color = colors[j])
	
	plt.legend(loc = "best")
	plt.show()

def LineChart(xAxis,yAxis,title = None,xLabel = None,yLabel = None,tabLabels = None,tabColors = None):
	'''xAxis bo tabela, yAxis pa touple podatkov, ki jih želimo narisati.'''
	if title != None:
		if not isinstance(title,str):
			raise ChartException("Chart title must be a string!")
		plt.title(title)

	if xLabel != None:
		if not isinstance(xLabel,str):
			raise ChartException("Label on x axis must be a string!")
		plt.xlabel(xLabel)

	if yLabel != None:
		if not isinstance(yLabel,str):
			raise ChartException("Label on y axis must be a string!")
		plt.ylabel(yLabel)

	plt.xticks(xAxis,map(str,xAxis))

	colors = None
	defaultColors = ["#3498EB","#9C3094","#E2E629","#3F5DE0","#F8271F"]
	if tabColors != None:
		if len(tabColors) != len(yAxis):
			raise ChartException("Number of colors must match the number of data sets!")
		colors = tabColors
	else:
		colorsNeeded = len(yAxis)
		if colorsNeeded > len(defaultColors):
			colorsToGenerate = colorsNeeded - len(defaultColors)
			generatedColors = []
			for _ in range(colorsToGenerate): #we randomly generate the remainder of the missing colors
				generatedColors.append("#" + "".join(map(str,r.sample("0123456789ABCDEF",6))))

			colors = defaultColors + generatedColors
		else:
			colors = defaultColors[:colorsNeeded]
			
	labels = None
	if tabLabels != None:
		if len(tabLabels) != len(yAxis):
			raise ChartException("Number of labels must match the number of data sets!")
		labels = tabLabels
	else: #defoult notation of labels
		labelsNeeded = len(yAxis)
		labels = [str(i) for i in range(1,labelsNeeded + 1)]
		
	for i in range(len(yAxis)):
			plt.plot(xAxis,yAxis[i],color = colors[i],label = labels[i])
	
	plt.legend(loc = "best")
	plt.show()
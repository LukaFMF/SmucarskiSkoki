import numpy as np
from sklearn import *
from datetime import *

def MAPE(values, predictions):
	error = 0
	for i in range(len(values)):
		if values[i] > 0:
			error += abs((values[i] - predictions[i]) / values[i])
	return error / len(values)

def PredictNextJump(athlete):
	
	data = []
	for res in athlete.personalResults:
		
		event = athlete.events[res[0]]
		competition = athlete.events[res[0]].competitions[res[1]]
		result = athlete.events[res[0]].competitions[res[1]].results[res[2]]

		if (len(res) == 3 and competition.hillSizeName == "FH" and
			((result.points1 != None and result.distance1 != None) or 
			(result.points2 != None and result.distance2 != None)) and 
			competition.hillSizeHeight != None):

			timestamp = datetime(competition.date.year,competition.date.month,competition.date.day).timestamp()

			if result.points1 != None:
				data.append([result.distance1,competition.hillSizeHeight, \
				float(result.country == event.country),float(timestamp),result.points1])
			if result.points2 != None:
				data.append([result.distance2,competition.hillSizeHeight, \
				float(result.country == event.country),float(timestamp),result.points2])
	
	data.sort(key = lambda x: x[-2])

	instances = [x[:-1] for x in data]
	values = [x[-1] for x in data]

	print(len(instances))

	percent = int(len(instances)*.8)

	trainInstances = instances[:percent]
	trainValues = values[:percent]

	testInstances = instances[percent:]
	testValues = values[percent:]

	regressor =  tree.DecisionTreeRegressor() # DT

	regressor.fit(trainInstances,trainValues)

	predictions = regressor.predict(testInstances)

	

	for i in range(len(testInstances)):
		print(f"Parameters:")
		# print(f"\tRank: {testInstances[i][0]:.0f}")
		print(f"\tDistance: {testInstances[i][0]:.1f}m")
		print(f"\tHill height: {testInstances[i][1]:.0f}")
		print(f"\tHome country?: {testInstances[i][2]:.0f}")
		print(f"\tTimestamp: {testInstances[i][3]:.0f}")
		print(f"Absolute difference: {abs(predictions[i] - testValues[i]):.2f}")
		print()


	print(f"Average relative error: {100 * MAPE(testValues, predictions):.2f}%")
	print(f"Average absolute error: {sum(map(lambda x,y: abs(x - y),testValues,predictions))/len(predictions):.2f}")
	# print("   Model |  MAPE")

	# for name, regressor in regressors.items():
	# 	regressor.fit(trainInstances, trainValues)
	# 	testPredictions = regressor.predict(testInstances)

	# 	print(f"{name:>8s} | {100 * MAPE(testValues, testPredictions):5.2f}%")
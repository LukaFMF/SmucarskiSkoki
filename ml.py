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
		if (len(res) == 3 and athlete.events[res[0]].competitions[res[1]].hillSizeName == "FH" and 
			athlete.events[res[0]].competitions[res[1]].results[res[2]].points1 != None and 
			athlete.events[res[0]].competitions[res[1]].results[res[2]].distance1 != None and 
			athlete.events[res[0]].competitions[res[1]].hillSizeHeight != None):

			event = athlete.events[res[0]]
			competition = athlete.events[res[0]].competitions[res[1]]
			result = athlete.events[res[0]].competitions[res[1]].results[res[2]]

			timestamp = datetime(competition.date.year,competition.date.month,competition.date.day).timestamp()

			data.append([float(res[2] + 1),result.distance1,competition.hillSizeHeight, \
			float(result.country == event.country),float(timestamp),result.points1])
			
	data.sort(key = lambda x: x[-2])

	instances = [x[:-1] for x in data]
	values = [x[-1] for x in data]

	print(len(instances))

	percent = int(len(instances)*.8)

	trainInstances = instances[:percent]
	trainValues = values[:percent]

	testInstances = instances[percent:]
	testValues = values[percent:]

	regressors = {"kNN": neighbors.KNeighborsRegressor(), "LR": linear_model.LinearRegression(), "DT": tree.DecisionTreeRegressor(), "RF": ensemble.RandomForestRegressor(max_depth = 20, n_estimators = 50), "SVM": svm.SVR(gamma = 'scale')}

	print("   Model |  MAPE")

	for name, regressor in regressors.items():
		regressor.fit(trainInstances, trainValues)
		testPredictions = regressor.predict(testInstances)

		print("{:>8s} | {:5.2f}%".format("'" + name + "'", 100 * MAPE(testValues, testPredictions)))
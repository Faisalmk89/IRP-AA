# helper functions 

import pandas as pd
import string

# arrange schedule output into data frame
def arrangeDF(N,T,Visiting_Time, Delivery_Quantity):
	t = range(1,T+1)
	customers = [string.ascii_uppercase[i] for i in range(N-1)]
	df = pd.DataFrame(index=t, columns=customers)
	df = df.fillna(0) 
	cusList = Visiting_Time.keys()
	for c in cusList:
		periods = Visiting_Time[c]
		delivery = Delivery_Quantity[c]
		for i,p in enumerate(periods):
			df[customers[c-2]][p] = delivery[i]
	return df

# arrange schedule sequence into data frame
def arrangeDFseq(N,T,PathEachTime):
	t = range(1,T+1)
	customers = [string.ascii_uppercase[i] for i in range(N-1)]
	df = pd.DataFrame(index=t, columns=customers)
	df = df.fillna('-') 
	timeList = PathEachTime.keys()
	for ti in timeList:
		path = PathEachTime[ti]
		for i,p in enumerate(path):
			if p>1: # always start from depot
				df[customers[p-2]][ti] = i
	return df
	


if __name__ == '__main__':

	from DtaSchedule import getSchedule
	from createRandom import genMatrices
	
	Nnew = 7
	T = 9
	cij,d_it,h_it = genMatrices(Nnew, T)
        Visiting_Time,Delivery_Quantity = getSchedule(Nnew,T,cij,d_it,h_it)
	df = arrangeDF(Nnew,T,Visiting_Time, Delivery_Quantity)
	print Visiting_Time
	print Delivery_Quantity
	print df

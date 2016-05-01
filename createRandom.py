import random, math

# given N customers (incl. depot), T planning periods
# simulate distance matrix cij, demand quantities d_it, and holding costs h_it

def genMatrices(N,T):
	# default parameters
	Beta_Inv = 1  # this is some factor to weight the inventory cost, we will need it for sensitivity analysis.
	Beta_Rout = 15  # this is some factor to weight the transportation cost, we will need it for sensitivity analysis.
	#  To generate the coordination of nodes in the graph of each node and then calculate the distance between each pair.
	a = 0
	b = 1000
	X = []
	Y = X
	for iiter in range(0, int(N), 1):
    		s1 = random.random()
    		s2 = random.random()
    		x = (b - a) * s1 + a
    		y = (b - a) * s2 + a
    		X.append(x)
    		Y.append(y)
	cij = []  # cost matrix of distances
	for iiter1 in range(len(X)):
    		cij.append([])
    		for iiter2 in range(len(Y)):
        		cij[iiter1].append(Beta_Rout * (((X[iiter1] - X[iiter2]) ** 2 + (Y[iiter1] - Y[iiter2]) ** 2) ** 0.5))  # math.floor
	# to generate demand quantities for each customer for each planning period.
	a = 30
	b = 50
	d_it = []
	for iiter1 in range(0, N):
    		d_it.append([])
    		for iiter2 in range(0, T):
        		if iiter1 == 0:
            			d_it[iiter1].append(0)
        		else:
            			d_it[iiter1].append(math.floor((b - a) * random.random() + a))
	# to generate holding cost for each customer.
	a = 3
	b = 8
	h_it = []
	for iiter1 in range(0, N):
    		h_it.append([])
    		for iiter2 in range(0, T):
        		if iiter1 == 0:
            			h_it[iiter1].append(0)
        		else:
            			h_it[iiter1].append(math.floor((b - a) * random.random() + a))
	return cij, d_it, h_it






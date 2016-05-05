# input N, T, distance matrix cij, demand quantities d_it, and holding costs h_it
# output Visiting_Time, Delivery_Quantity

import math
import random
import time

def getSchedule(N,T,cij,d_it,h_it):

	L = math.floor(math.log1p(T))  # why it was -1
	Nodes = N * (L + 1) + 1  # plus one for the artificial node
	Roots = 0

	# from now and on the coding of the approximation algorithm.

	###################
	Visits = {}
	for key in range(0, int(L + 1)):
		Var = int(math.floor(T / 2 ** key))
		LLo = []
		for x in range(1, Var + 1):
		    LLo.append(float(x) * 2 ** key)
		if key >= 1:
		    Visits.update({key: [1.0] + LLo})
		else:
		    Visits.update({key: LLo})

	Visit_Scheduling = {}
	A = [range(1, T + 1), [0] * T]
	Mat = [range(1, T + 1), [0] * T]

	for key in range(len(Visits)):
		Vs = Visits[key]
		Counter = 0
		for j in Vs:
		    while A[0][Counter] <= j:
		        A[1][Counter] = j
		        Counter += 1
		        if Counter >= T:
		            break
		for i2 in range(len(A[0])):
		    if A[1][i2] == 0:
		        A[1][i2] = T
		Visit_Scheduling.update({key: A})

		A = [range(1, T + 1), [0] * T]

	Inv_Level = {}  # this dictionary will store the inventory level for each
	#  customer for each planning period for each delivery scheduling
	#  the structure will be a bit tricky since we ca't build a dictionary with three items.
	#  so customer for each scheduling for each time.
	for customer in range(1, N + 1):
		for Sche in range(0, int(L + 1)):
		    key = (customer - 1) * int(L + 1) + Sche + 1
		    Mat = []
		    for time in range(T):
		        Rng = Visit_Scheduling[Sche]
		        Str = Rng[0][int(time)] - 1
		        EnD = int(Rng[1][int(time)])
		        Level = sum(d_it[int(customer - 1)][Str:EnD]) - d_it[customer - 1][time]
		        LevelCost = Level * h_it[customer - 1][time]
		        Mat.append(LevelCost)
		    Val = sum(Mat)
		    Inv_Level.update({key: Val})  # by this, the holding cost of each node is ready. i.e. penalty of each node.

	Inv_Level.update({0: 0})
	Cij = {}  # this dictionary will be the cij between nodes in the GW algorithm.
	Dummycij = []

	for key in range(int(L + 1)):
		for iiter in range(len(cij)):
		    Dummycij.append([])
		    for iiter2 in range(len(cij[0])):
		        Dummycij[iiter].append(cij[iiter][iiter2] * (math.ceil(math.floor(T / 2 ** (key + 1) / 2))))

		Cij.update({key: Dummycij})
		Dummycij = []

	Groups_Members = {}
	Keys = ['dv', 'wv', 'lambda_v']
	d_v = [0] * int(Nodes)
	for iiter in range(int(Nodes)):
		if iiter == 0:
		    Groups_Members.update({iiter: {'Members': [iiter], 'Lambda': 0, 'w': 0}})
		else:
		    Groups_Members.update({iiter: {'Members': [iiter], 'Lambda': 1, 'w': 0}})

	# lines 3 to 8 of GW PCST
	RCij = []  # this matrix will be helpful for creating the RCij, which is the distance between each two nodes in the
	# GW algorithm
	for i in range(int(N * (L + 1) + 1)):
		RCij.append([])
		for j in range(int(N * (L + 1) + 1)):
		    RCij[i].append(99.0 * 10 ** 99)
	for i in range(N + 1):
		RCij[i][i] = 0

	for k in range(int(L + 1)):
		for i in range(1, N + 1):
		    for j in range(1, N + 1):
		        RCij[k * N + i][k * N + j] = cij[i - 1][j - 1]

	# Now I will start implementing the GW algorithm based on my pseudo-code
	F = []  # line 1, empty forest.
	# Groups_Members is the list where we have the group member nodes, lambda value of that group of nodes and w.
	# the value of d(v) is stored in a separate list.

	for j in range(int((L + 1))):
		RCij[0][j * N + 1] = 0
		RCij[j * N + 1][0] = 0

	Flag = 1
	Counter = 0
	while Flag == 1:
		Epsilon1 = 99999 ** 10.0
		EdgeFrom = []
		for i in list(Groups_Members.keys()):
		    for j in list(Groups_Members.keys()):  # go though all groups one by one such that they are different
		        if i != j:
		            if (Groups_Members[i]['Lambda'] + Groups_Members[j]['Lambda']) > 0:

		                for ii in Groups_Members[i]['Members']:
		                    for jj in Groups_Members[j]['Members']:
		                        eps1 = (float(RCij[ii][jj]) - d_v[ii] - d_v[jj]) / (Groups_Members[i]['Lambda'] +
		                                                                            Groups_Members[j]['Lambda'])
		                        if eps1 <= Epsilon1:
		                            Epsilon1 = eps1
		                            Edge = [ii, jj]
		                            EdgeFrom = [i, j]  # calculation of epsilon and store the edge information
		                            EdgeFrom.sort()

		# moving to epsilon 2 part calculation
		Epsilon2 = 99999 ** 10.0
		for i in list(Groups_Members.keys()):
		    if Groups_Members[i]['Lambda'] == 1:
		        DummyVal = 0
		        for s in Groups_Members[i]['Members']:
		            DummyVal += Inv_Level[s]
		        eps2 = DummyVal - Groups_Members[i]['w']
		        DummyVal = 0
		        if eps2 <= Epsilon2:
		            Cbar = i
		            Epsilon2 = eps2

		Eps = min(Epsilon2, Epsilon1)

		for i in list(Groups_Members.keys()):
		    Groups_Members[i]['w'] += Eps * Groups_Members[i]['Lambda']  # line 13 of my pseudo code

		for i in list(Groups_Members.keys()):
		    if Groups_Members[i]['Lambda'] == 1:
		        for memberz in Groups_Members[i]['Members']:
		            d_v[memberz] += Eps * Groups_Members[i]['Lambda']
		if Epsilon2 == Eps:
		    Groups_Members[Cbar]['Lambda'] = 0  # line 19, there is something missing though
		else:
		    F.append([])
		    F[Counter].append(Edge)
		    Counter += 1
		    Groups_Members[EdgeFrom[0]]['Members'] = Groups_Members[EdgeFrom[0]]['Members'] \
		                                             + Groups_Members[EdgeFrom[1]]['Members']
		    Groups_Members[EdgeFrom[0]]['w'] = Groups_Members[EdgeFrom[0]]['w'] + Groups_Members[EdgeFrom[1]]['w']
		    Groups_Members.pop(EdgeFrom[1], None)
		    if 0 in Groups_Members[EdgeFrom[0]]['Members']:
		        Groups_Members[EdgeFrom[0]]['Lambda'] = 0
		    else:
		        Groups_Members[EdgeFrom[0]]['Lambda'] = 1

		DummyValue = 0
		for i in list(Groups_Members.keys()):
		    DummyValue += Groups_Members[i]['Lambda']
		if DummyValue == 0:
		    Flag = 0

	GW_Result = Groups_Members[0]['Members']
	GW_Result.sort()
	GW_Result.pop(0)

	Nodz_Scheduling = {}
	for key in range(int(L + 1)):
		Nodz_Scheduling.update({key: []})

	for iiter in GW_Result:
		NodeSche = math.floor(float(iiter) / N)
		Lisht = range(int(L + 2))
		if iiter % N == 0:
		    Node2 = N
		else:
		    Node2 = iiter % N
		if math.floor(float(iiter) / N) > L:
		    Val = int(math.floor(float(iiter) / N)) - 1
		else:
		    Val = int(math.floor(float(iiter) / N))
		if iiter % N == 0 and math.floor(float(iiter) / N) <= L:
		    Val -= 1
		# by this we converted the set of nodes from the GW graph to the original graph.
		# Now let us create a dictionary for each scheduling \in L and put the nodes following each scheduling.
		Mat = Nodz_Scheduling[Val]
		Mat.append(Node2)
		Nodz_Scheduling.update({Val: Mat})  # by now we calculated the Q_i and G_i

	SQ = {}
	for i in range(int(L) + 1):
		SQ.update({i: []})

	Customers = range(1, N + 1, 1)
	RV = reversed(Nodz_Scheduling.keys())
	Refill_Time = {}  # this dictionary will have a key for each customer with its name, then the value of that key is the
	#  times to visit that customer.
	for i in RV:
		Elements = Nodz_Scheduling[i]
		Mat = []
		Prev_Iter_List = Customers
		Counter = int(len(Prev_Iter_List)) - 1
		while Counter >= 0:
		    if Prev_Iter_List[Counter] in Elements:
		        Mat.append(Prev_Iter_List[Counter])
		        SQ.update({i: Mat})
		        Refill_Time.update({Prev_Iter_List[Counter]: i})
		        Customers.remove(Prev_Iter_List[Counter])
		        Counter -= 1
		    else:
		        Counter -= 1
	Served = Refill_Time.keys()
	for i in range(1, N + 1):
		if i not in Served:
		    Refill_Time.update({i: int(L)})

	for i in SQ.keys():
		if len(SQ[i]) > 0 and 1 not in SQ[i]:
		    Mat = SQ[i]
		    Mat.append(1)
		    SQ.update({i: Mat})
	# Now let us establish the scheduling of visits for each customer:
	Visiting_Time = {}
	Delivery_Quantity = {}
	for i in range(2, N + 1):
		t = Refill_Time[i]
		Mot = []
		Mat = [1]  # always visit customer at period 1.
		for j in range(1, int(math.floor(T / 2 ** t) + 1)):
		    Mat.append(j * 2 ** t)
		    Mot.append(sum(d_it[i - 1][Mat[j - 1]: Mat[j]]))
		if Mot.count(1) > 1:
		    Mot.pop(1)
		Mot.append(sum(d_it[i - 1][Mat[j]: int(T)]))
		Visiting_Time.update({i: Mat})
		Delivery_Quantity.update({i: Mot})

	#  Now let us establish the trees connecting nodes in each round.
	NodzEachTime = {} # key is time and value is nodz
	Ll = Visiting_Time.keys()
	for t in range(int(T)):
		TempList = [1]  # this is one since the depot has to be within the route.
		for Nodz in Ll:
		    if t in Visiting_Time[Nodz]:
		        TempList.append(Nodz)
		if len(TempList) > 1:
		    NodzEachTime.update({t: TempList})

	# Given we have the nodes to visit each time, now we need to establish a tree connecting the nodes visited each time.
	PathEachTime = {}
	for iiter in NodzEachTime.keys():
		Nodz = NodzEachTime[iiter]
		i = Nodz[0]
		Nodz.remove(i)
		Path = [1]
		while len(Nodz) > 0:
		    cijprime = []
		    for k in Nodz:
		        cijprime.append(cij[i - 1][k - 1])
		    j = Nodz[cijprime.index(min(cijprime))]
		    Path.append(j)
		    i = Nodz.index(j)
		    b = Nodz[i]
		    Nodz.remove(b)
		PathEachTime.update({iiter: Path})

	return Visiting_Time, Delivery_Quantity, PathEachTime

	

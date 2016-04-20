import math
import random
import time
start_time = time.time()

print "Hello world! "
# using this file we will start processing the data, first let assume that the data will be random points.
Beta_Inv = 1
Beta_Rout = 1
N = 7  # number of customers in each instance plus the depot.
T = 9  # Number of planning periods
L = math.floor(math.log1p(T - 1))
Nodes = N * (L + 1) + 1  # plus one for the artificial node
Roots = 0

#  To generate the coordination of nodes in the graph, deamnd, and holding cost of each node.

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
        cij[iiter1].append(
            Beta_Rout * (((X[iiter1] - X[iiter2]) ** 2 + (Y[iiter1] - Y[iiter2]) ** 2) ** 0.5))  # math.floor

# to generate demand quantities
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

# to generate holding cost
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
# for the time being we will not make Cij, instead we will update the cost of Cij elements on site for GW Algorithm

Visits = {}
for key in range(0, int(L + 1)):
    Var = int(math.floor(T / 2 ** key))
    LLo = []
    # print key
    for x in range(1, Var + 1):
        LLo.append(float(x) * 2 ** key)
    if key >= 1:
        Visits.update({key: [1.0] + LLo})
    else:
        #  del LLo[-1]
        Visits.update({key: LLo})

#  print Visits

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

# print d_it
#  print sum(d_it[int(5 - 1)][0:0])
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
            LevelCost = Level * h_it[customer-1][time]
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
    # print len(Groups_Members)
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
print Groups_Members


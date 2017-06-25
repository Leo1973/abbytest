import copy

class module_input:
    def __init__(self, B, D, S, N, H, X, l_equipment):
        self.d_Blevel = B
        self.l_Distance = D
        self.f_S = S
        self.d_Number = N
        self.l_X = X
        self.f_T = self.getTime(self.l_X, l_equipment)
        self.f_h0 = H
    def getTime(self, X, l_equipment):
        a = 0.00
        b = 0.00
        for e in l_equipment:
            xi = X[e.d_ID % 10]
            a += xi * e.f_Force * e.f_ArriveTime
            #print a
            b += xi * e.f_Force
            #print b
        if b != 0:
            T = (a + self.f_S) / b
        else:
            T = 0
        print "coverT is: ", T
        return T

class equipment:
    def __init__(self, ID, V, N, F, P, T, C, B, L, module_input):
        self.d_ID = ID
        self.f_Velocity = V
        self.d_Number = N
        self.f_Force = F
        self.f_probility = P
        self.f_Time = T
        self.d_Cost = C
        self.d_Blevel = B
        self.d_Limit = L
        self.f_ArriveTime = self.getArriveTime(module_input)
        self.f_CoverS = self.getCoverS(module_input)
    def getArriveTime(self, module_input):
        group = int(self.d_ID/10)
        return module_input.l_Distance[group-1]/self.f_Velocity
    def getCoverS(self, module_input):
        xi = module_input.l_X[self.d_ID % 10]
        print "CoverS is: ", (module_input.f_T - self.f_ArriveTime) * self.f_Force * xi 
        return (module_input.f_T - self.f_ArriveTime) * self.f_Force * xi

def checkConstraint(module, equipment):
    Cost = 0
    Number = 0
    k = 0
    flag = 0
    while k < equipment.__len__():
        temp_X = module.l_X[k]
        temp_E = equipment[k]
        Cost += temp_X * temp_E.d_Cost
        Number += temp_X * temp_E.d_Number
        if temp_E.f_Force > 0:
            flag += temp_X
        if temp_E.d_Blevel < module.d_Blevel and temp_X > 0: 
            print "IF ", temp_E.d_Blevel, " < ", module.d_Blevel, "and X:", temp_X
            return False
        if temp_X > temp_E.d_Limit:
            print "IF ",temp_X, " > ", temp_E.d_Limit
            return False
        #if temp_E.f_ArriveTime > module.f_h0:
            #return False
        k += 1
   
    if module.d_Number > Number or flag == 0:
        print "IF ", module.d_Number, ">", Number, "and FLAG", flag
        return False
    else:
        #print module.d_Number, Number
        return Cost
#a = module_input(1,2,3,4,5,6)
#print a.d_T
#equipment

def caculatePOS(module, equipment):
    POS = 0
    k = 0
    while k < equipment.__len__():
        temp_E = equipment[k]
        #print temp_E.f_CoverS, module.f_S, temp_E.f_probility
        POS += (temp_E.f_CoverS / module.f_S) * temp_E.f_probility
        print "temp_E.f_CoverS, module.f_S, temp_E.f_probility: ", temp_E.f_CoverS, module.f_S, temp_E.f_probility
        print "POS is: ", POS
        k += 1
    return POS
def caculatePOE(module, equipment, POS):
    ET1 = caculateEt1(module, equipment)
    ET2 = caculateEt2(module, equipment, POS)
    POE = (module.f_h0 / module.d_Blevel)/(ET1 + ET2)
    return POE
def caculatePOR(module, equipment):
    POS = caculatePOS(module, equipment)
    POE = caculatePOE(module, equipment, POS)
    POR = POS*POE
    return POR
def caculateEt1(module, equipment):
    #print equipment
    k = 0
    s = 0
    S = 0
    while k < equipment.__len__() - 1:
        temp_E = equipment[k]
        temp_X = module.l_X[k]
        if equipment[k].f_Force > 0:
            if equipment[k+1].f_Force > 0:
                s += temp_E.f_Force * temp_X
                S += s * (( equipment[k+1].f_ArriveTime ** 2) - (temp_E.f_ArriveTime ** 2)) / (2 * module.f_S )
            else:
                s += temp_E.f_Force * temp_X
                S += s * (( module.f_T ** 2) - (temp_E.f_ArriveTime ** 2)) / (2 * module.f_S )
        k += 1
    return S
def caculateEt2(module, equipment, POS):
   #print equipment
    l_N = []
    N = int(POS * module.d_Number)
    print "N is: ", N
    #print N
    #print equipment
    for i in range(equipment.__len__()):
        l_N.append(equipment[i].d_Number * module.l_X[i])
    #print l_N
    column = l_N.__len__()
    Et2_matrix = []
    temp_matrix = [0]*column
    minT = 9999
    while notbeyondBound(temp_matrix, l_N):
        #print temp_matrix
        if isOK(temp_matrix, N, equipment):
            #print temp_matrix
            #print caculateMinT(temp_matrix, equipment)
            temp = copy.deepcopy(temp_matrix)
            Et2_matrix.append(temp)
        add1(temp_matrix, l_N)
    print Et2_matrix
    for matrix in Et2_matrix:
        print "caculateMinT is: ", caculateMinT(matrix, equipment)
        if caculateMinT(matrix, equipment) < minT:
            minT = caculateMinT(matrix, equipment)
            index = copy.deepcopy(matrix)
    print "index is :", index
    #print minT
    #return index
    S = 0
    for i in range(index.__len__()):
        S += index[i]*equipment[i].f_ArriveTime
        print "i is : ", index[i], "arrive time is : ", equipment[i].f_ArriveTime
        x = 0
        for j in range(index[i]):
            x += j+1
        print "x is : ", x
        if module.l_X[i] != 0:
            S += (x*equipment[i].f_Time / module.l_X[i])
        print "S is: ", S
    S /= N
    return S

def notbeyondBound(temp_matrix, l_N):
    for i in range(l_N.__len__()):
        #print "temp_matrix[i]: ", temp_matrix[i], "l_N[i]: ", l_N[i]
        if temp_matrix[i] > l_N[i]:
            return False
    return True

def add1(temp_matrix, l_N):
    i = -1
    temp_matrix[i] += 1
    while not notbeyondBound(temp_matrix, l_N) and i > -l_N.__len__():
        temp_matrix[i] = 0
        i -= 1
        temp_matrix[i] += 1
    return temp_matrix

def isOK(temp_matrix, N, equipment):
    S = 0
    for n in temp_matrix:
        S += n
    if S == N:
        #print temp_matrix
        return True
    else:
        return False

def caculateMinT(temp_matrix, equipment):
    length = range(temp_matrix.__len__())
    flag = 0
    minx = 0
    for i in range(temp_matrix.__len__()):
        if temp_matrix[i]>0:
            #print "equipment id", equipment[i].d_ID, "TIME ",   equipment[i].f_ArriveTime
            mid = equipment[i].f_ArriveTime + temp_matrix[i]*equipment[i].f_Time
            if mid > minx:
                minx = mid
    return minx
            #print length
            #temp = copy.deepcopy(length)
            #temp.__delitem__(i)
            #print temp
            #print "i is", i
            #for t in temp:
                #print "t is ", t
                #if temp_matrix[t] > 0:
                    #print "t is:", t, "I is "
                    #left = equipment[t].f_ArriveTime + ( temp_matrix[t] - 1 )*equipment[t].f_Time
                    #right = equipment[t].f_ArriveTime + ( temp_matrix[t] + 1 )*equipment[t].f_Time
                    #print temp_matrix
                    #print "left is",left, "mid is ", mid, "right is ", right
                    #if left <= mid
                        #flag += 0
                    #else:
                        #flag = 1
    #if flag == 0:
        #return True
    #else:
        #return False



    
def Reload(equip, mB, mD, mS, mN, mH, X, E):
    E = []
    module = module_input(mB, mD, mS, mN, mH, X, E)
    for e in equip:
        eID, eV, eN, eF, eP, eT, eC, eB, eL = e
        E.append(equipment(eID, eV, eN, eF, eP, eT, eC, eB, eL, module))
    if not checkConstraint(module, E):
        print "Constraint Failed"
        return 0, 0

#for e in l_equipment:
    #print e.d_ID
#    print e.d_ArriveTime
    module = module_input(mB, mD, mS, mN, mH, X, E)
#print module.f_T
    E = []
    for e in equip:
        eID, eV, eN, eF, eP, eT, eC, eB, eL = e
        E.append(equipment(eID, eV, eN, eF, eP, eT, eC, eB, eL, module))
   #print E
    return module, E
"""
#         ID   V       N   F   P   T  C   B  L
equip = [[10, 324.00, 0, 30, 0.9, 0, 1, 4, 8],
         [11, 287.00, 0, 40, 0.95, 0, 2, 3, 8],
         [12, 15.00, 50, 0, 0, 0.04, 50, 4, 8],
         [23, 30.00, 10, 0, 0, 0.08, 10, 4, 8],
         [34, 25.00, 15, 0, 0, 0.1, 15, 3, 8]]

#                    B    D           S    N   H   
mB, mD, mS, mN ,mH= [4, [50,100,30], 100, 20, 2.2]
X = [1,1,1,1,1]
"""

equip = [[10, 220.00, 0, 100, 0.95, 0,    3,   4, 3],
         [21, 280.00, 0, 120, 0.8,  0,    5,  4, 4],
         [32, 300.00, 0, 130,   0.9,    0, 7,   4, 2],
         [13, 480.00, 0, 180,   0.85,    0, 10,   5, 3],
         [34, 620.00, 0, 240,   0.91,    0, 16,   5, 3],
         [25, 18.00, 40, 0,   0,    0.04, 20,   4, 2],
         [16, 39.00, 10, 0,   0,    0.1, 10,   4, 5],
         [17, 32.15, 20, 0,   0,    0.12, 16,   5, 3],
         [18, 28.00, 6, 0,   0,    0.02, 9,   4, 5],
         [29, 30.00, 20, 0,   0,    0.06, 17,   5, 3],
        ]
mB, mD, mS, mN, mH = [4, [30, 60, 80], 500, 40, 2.2]
X = [0,0,0,0,0,0,0,0,0,0]
E = []
i = 0
def Read(equip, mB, mD, mS, mN, mH, X, E):
    module, E = Reload(equip, mB, mD, mS, mN, mH, X, E) 
    global i
#print E
#print checkConstraint(module, E)
    if module != 0 and E != 0:
        for e in E:
            print "arriveTime is: ", e.f_ArriveTime
        POS = caculatePOS(module, E)
        ET1 = caculateEt1(module, E)
        ET2 = caculateEt2(module, E, POS)
        POE = caculatePOE(module, E, POS)
        POR = caculatePOR(module, E)
        COST = checkConstraint(module, E)
        print "COST IS: ", COST
        print "POS IS: ", POS
        print "ET1 IS: ", ET1
        print "ET2 IS: ", ET2
        print "POE IS: ", POE
        print "POR IS: ", POR
        print "No: ", i
        i += 1
        return POR, COST
    else:
        return 0, 0
l_X = []
Bound = []
for e in equip:
    Bound.append(e[-1])
print "Bound is: ", Bound
while notbeyondBound(X, Bound):
    temp = copy.deepcopy(X)
    l_X.append(temp)
    add1(X, Bound)
print l_X
fp = open("moduleout", 'w')
for x in l_X:

#X = [1,1,1,1]
    POR, COST = Read(equip, mB, mD, mS, mN, mH, x, E)
    if POR != 0 and COST != 0:
        fp.write("#"+str(x)+"\n")
        fp.write(str(POR)+" "+str(COST) +"\n")

fp.close()


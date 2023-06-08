### TEAM MEMBERS
## MEMBER 1: 210050027
## MEMBER 2: 210050055
## MEMBER 3: 210050147

from z3 import *
import sys

file = sys.argv[1]

with open(file) as f:
	n,T = [int(x) for x in next(f).split()]
	matrix = []
	for line in f:
		matrix.append([int(x) for x in line.split()])

# s is used as z3-sat-solver
s = Solver()

# Initialising nxnxT matrix representing (i,j) element after k moves
matr = [[[Int(f'cell_{i}_{j}_{k}') for k in range(T+1)] for j in range(n)] for i in range(n)]
# Initialising nxT matrix representing ith upward movement of jth column
up = [[Bool(f'up_{i}_{j}') for j in range(T)] for i in range (n)]
# Initialising nxT matrix representing ith downward movement of jth column
down = [[Bool(f'down_{i}_{j}') for j in range(T)] for i in range (n)]
# Initialising nxT matrix representing ith right movement of jth row
right = [[Bool(f'right_{i}_{j}') for j in range(T)] for i in range (n)]
# Initialising nxT matrix representing ith left movement of jth row
left = [[Bool(f'left_{i}_{j}') for j in range(T)] for i in range (n)]

# Condition to not allow reverse move on same row/column.
# Similarly for other possible cases.
for i in range(T-1):
    for j in range(n):
        s.add(Or(Not(up[j][i]), Not(down[j][i+1])))
        s.add(Or(Not(down[j][i]), Not(up[j][i+1])))
        s.add(Or(Not(left[j][i]), Not(right[j][i+1])))
        s.add(Or(Not(right[j][i]), Not(left[j][i+1])))

# Adding the initial condition of the matrix to solver.
for i in range(n):
    for j in range(n):
        s.add((matr[i][j][0] - int(matrix[i][j])) == 0)

# Adding all possible solved condition of matrix to solver
solved_condition = []
for k in range(T+1):
    done_curr = []
    for i in range(n):
        for j in range(n):
            done_curr.append(matr[i][j][k] - int(i*n + j + 1) == 0)
    solved_condition.append(And(done_curr))  
           
# Adding condtion that at jth move only one of 4*n possible moves is allowed.
cond = []
for j in range(T):
    temp = []
    for i in range(n):
        temp.append(down[i][j])
        temp.append(up[i][j])
        temp.append(right[i][j])
        temp.append(left[i][j])
    temp1 = [ Sum ([If ( i , 1, 0 )for i in temp]) == 1]
    s.add(And(temp1))

# Adding all possible moves along with their effects on matrix.
# For Left move
rotate_effects = []
for k in range(T):
    for c in range (n):
        curr_cond = []
        for i in range (n):
            for j in range (n):
                if(i == c):
                    curr_cond.append(matr[i][j][k + 1] - matr[i][(j+1)%n][k] == 0)
                else:
                    curr_cond.append(matr[i][j][k+1] - matr[i][j][k] == 0)
    
        rotate_effects.append(Or ( Not(left[c][k]) , And(curr_cond)))
# For Right move
for k in range(T):
    for c in range (n):
        curr_cond = []
        for i in range (n):
            for j in range (n):
                if(i == c):
                    curr_cond.append(matr[i][j][k + 1] - matr[i][(j - 1)%n][k] == 0)
                else:
                    curr_cond.append(matr[i][j][k+1] - matr[i][j][k] == 0)
    
        rotate_effects.append(Or ( Not(right[c][k]) , And(curr_cond)))
# For Up move      
for k in range(T):
    for c in range (n):
        curr_cond = []
        for i in range (n):
            for j in range (n):
                if(j == c):
                    curr_cond.append(matr[i][j][k + 1] - matr[(i + 1)%n][j][k] == 0)
                else:
                    curr_cond.append(matr[i][j][k+1] - matr[i][j][k] == 0)
    
        rotate_effects.append(Or ( Not(up[c][k]) , And(curr_cond)))
# For Down move      
for k in range(T):
    for c in range (n):
        curr_cond = []
        for i in range (n):
            for j in range (n):
                if(j == c):
                    curr_cond.append(matr[i][j][k + 1] - matr[(i - 1)%n][j][k] == 0)
                else:
                    curr_cond.append(matr[i][j][k+1] - matr[i][j][k] == 0)
    
        rotate_effects.append(Or ( Not(down[c][k]) , And(curr_cond)))                        
# Adding all rotation effects to solver     
s.add(And(rotate_effects))  
# Adding all solved condition to solver                            
s.add(Or(solved_condition))      
# Checking if the given problem is sat or unsat
x = s.check()
print(x)

# If sat then printing appropraite moves based on model.
if x == sat:
    m = s.model()
    le = [[ m.evaluate(left[i][j]) for j in range(T)] for i in range(n)]
    ri = [[ m.evaluate(right[i][j]) for j in range(T)] for i in range(n)]
    up_ = [[ m.evaluate(up[i][j]) for j in range(T)] for i in range(n)]
    do = [[ m.evaluate(down[i][j]) for j in range(T)] for i in range(n)]
    matrix_val = [[[ m.evaluate(matr[i][j][k]) for k in range(T+1)] for j in range(n)] for i in range(n)]
        
    done_res = []
    for k in range(T+ 1):
        curr = []
        for i in range(n):
            for j in range(n):
                curr.append(matrix_val[i][j][k] - int(n*i+j+1) == 0)
        
        s1 = Solver()
        s1.add(And(curr))
        y = s1.check()
        if(y == sat):
            done_res.append(True)
        else:
            done_res.append(False)                
    to_end = False

    if(not done_res[0]):
        for j in range(T):
            if(to_end):
                break
            for i in range(n):
                if(done_res[j]):
                    to_end = True
                    break
                if(le[i][j]):
                    print(str(i) + "l")
                if(ri[i][j]):
                    print(str(i) + "r")
                if(up_[i][j]):
                    print(str(i) + "u")
                if(do[i][j]):
                    print(str(i) + "d")                        
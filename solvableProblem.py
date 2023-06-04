import pulp

T = [
     'Everton',
     'LeicesterCity',
     'Liverpool',
     'ManchesterCity',
     'ManchesterUnited',
     'NewcastleUnited',
     ]

Liverpool = ['Liverpool', 'Everton']
Manchester = ['ManchesterCity', 'ManchesterUnited']

W = range(1, 2*len(T) - 1)
W2 = range(1, 2*len(T) - 2)
W3 = range(1, 2*len(T) - 5)
WFH = range(1, len(T))
WSH = range(len(T), 2*len(T) - 1)

x = pulp.LpVariable.dicts('x', (T, T, W), cat=pulp.LpBinary)
y = pulp.LpVariable.dicts('y', (T, W2), cat=pulp.LpBinary)

# Team cannot play itself
for w in W:

    for h in T:

        for a in T:

            if h == a:

                del x[h][a][w]

schedule = pulp.LpProblem("Schedule", pulp.LpMinimize)

schedule += pulp.lpSum(y[i][w] for w in W2 for i in T)

# Each team plays exactly one match each week
for w in W:

    for i in T:

        schedule += pulp.lpSum(x[i][a][w] for a in T if a != i) + \
            pulp.lpSum(x[h][i][w] for h in T if h != i) == 1

# Teams play each other twice during the season, with one home match and one away match
li = []
for i in T:
    li.append(i)
    for j in T:
        if j != i and j not in li:
            # team i plays one match in the first half against team j
            schedule += pulp.lpSum(x[i][j][w] for w in WFH) + \
                pulp.lpSum(x[j][i][w] for w in WFH) == 1
            # team i plays one match in the second half against team j
            schedule += pulp.lpSum(x[i][j][w] for w in WSH) + \
                pulp.lpSum(x[j][i][w] for w in WSH) == 1
            # if team i played at home against team j in the first half,
            # they will play away against team j in the second half, and vice versa
            schedule += pulp.lpSum(x[i][j][w] for w in WFH) == pulp.lpSum(
                x[j][i][w] for w in WSH)
            schedule += pulp.lpSum(x[j][i][w] for w in WFH) == pulp.lpSum(
                x[i][j][w] for w in WSH)

# First two and last two games cannot be consecutive away or home matches
for i in T:
    schedule += pulp.lpSum(x[i][j][W[0]] for j in T if i != j) + \
        pulp.lpSum(x[i][j][W[1]] for j in T if i != j) == 1
    schedule += pulp.lpSum(x[i][j][W[-1]] for j in T if i != j) + \
        pulp.lpSum(x[i][j][W[-2]] for j in T if i != j) == 1

# Teams from the same city can't play both home in the same week
for w in W:
    schedule += pulp.lpSum(x[h][a][w] for a in T for h in Liverpool if h != a) == len(Liverpool) // 2

for w in W:
    schedule += pulp.lpSum(x[h][a][w] for a in T for h in Manchester if h != a) == len(Manchester) // 2

# Sequencing rule
for i in T:
    for w in W3:
        schedule += pulp.lpSum(x[i][j][w] + x[i][j][w + 1] + x[i][j][w + 2] + x[i][j][w + 3] + x[i][j][w + 4]
                               for j in T if i != j) <= 3
        schedule += pulp.lpSum(x[i][j][w] + x[i][j][w + 1] + x[i][j][w + 2] + x[i][j][w + 3] + x[i][j][w + 4]
                               for j in T if i != j) >= 2

# Minimize the number of consecutive home and away games
for i in T:
    for w in W2:
        schedule += pulp.lpSum(x[i][j][w] + x[i][j][w + 1] for j in T if i != j) - y[i][w] <= 1     

schedule.solve()

file_open = open('6team_solution.sol', 'w')

for w in W:

    for h in T:

        for a in T:

            if a != h:
                file_open.write(f'{x[h][a][w].getName()} {int(x[h][a][w].value())}\n')
                if x[h][a][w].value() == 1.0:
                    home, away, week = x[h][a][w].getName().split('_')[1:]
                    print(f'Week: {week}  {home} vs. {away}')

    print()

file_open.close()
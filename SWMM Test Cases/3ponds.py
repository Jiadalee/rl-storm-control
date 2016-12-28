import swmm
import matplotlib.pyplot as plt
import numpy as np


def open2discrete(opening):
    """Discrete Ponds"""
    index_discrete = 0.01
    opening = float(opening)/index_discrete
    opening = int(np.floor(opening))
    return opening


def height2discrete(height):
    """Discrete Ponds"""
    index_discrete = 0.025
    height = float(height)/index_discrete
    height = int(np.floor(height))
    return height

def epsi_greedy(matrix, epsilon, state):
    """Action Value Function"""
    if np.random.rand() < epsilon:
        action = np.random.randint(0,10)
        action = action/10.0
    else:
        action = np.argmax(matrix[state, ])
        action = action * 0.01
    return action # Percent opening

#def reward(flow):
#    """Flow from the outlet"""
#    if flow >= 1.80 and flow < 2.0:
#        return 10.0
#    else:
#        return 0.0


def reward(height, outflow):
    """Reward Function"""
    if height >= 2.90 and height <= 2.950:
        if outflow > 0 and outflow <= 100:
            return 100.0
        else:
            return 0.0
    elif height >= 2.950 and height < 4.00:
        return -10.0 #(height-3.950)*100.0*(1/0.70)
    elif height >= 4.00:
        return -100.0
    elif height < 2.90:
        return (2.90-height)*(1/2.90)*100.0
    else:
        return 0.0

Q_matrix = np.zeros(shape=(200,101))

ALPHA = 0.006
GAMMA = 0.6
EPISODES = 2

flow = []
rewq=[]
depth =[]
for i in range(0, EPISODES):
    #SWMM input file
    INP = 'Testcase.inp'
    swmm.initialize(INP)
    # Physical Parameters to NULL --> Update to file
    state = 0 # Initial State
    t = 0
    rew= []
    volume= []
    dep =[]
    epsi = 0.6
    while t < 4000 :
        # 1. Choose a action
        height = swmm.get('S3', swmm.DEPTH, swmm.SI)
        height = height2discrete(height)
        state = height
        epsi = 0.99*epsi
        act = epsi_greedy(Q_matrix, epsi, height)
        # 2. Implement Action
        swmm.modify_setting('R1', act)
        swmm.run_step() # Run SWMM Time step
        # 3. Receive Reward
        height = swmm.get('S3', swmm.DEPTH, swmm.SI)
        outflow = swmm.get('C1', swmm.FLOW, swmm.SI)
        r = reward(height,outflow)
        rew.append(r)
        # 4. Q-Matrix Update
        state_n =  swmm.get('S3', swmm.DEPTH, swmm.SI)
        action = open2discrete(act)
        Q_matrix[state, action] = Q_matrix[state,action] + ALPHA * (r + GAMMA*np.max(Q_matrix[state_n, ])-Q_matrix[state, action])
        state = state_n
        volume.append(swmm.get('C1', swmm.FLOW, swmm.SI))
        dep.append(swmm.get('S3',swmm.DEPTH,swmm.SI))
        t = t + 1
    #ERRORS = swmm.finish()
    swmm.close()
    rewq.append(np.mean(rew))
    flow.append(np.mean(volume))
    depth.append(np.mean(dep))
np.savetxt("Q_matrix.txt", Q_matrix)


plt.figure(1)
plt.imshow(Q_matrix)
plt.axes().set_aspect('auto')
plt.colorbar()

plt.figure(2)
plt.plot(rewq)
plt.title('Average Reward')

plt.figure(3)
plt.plot(depth)
plt.title('Average Depth')

plt.figure(4)
plt.plot(dep)
plt.title('Depth_Final')
plt.show()




from qhdopt import QHD
from utils import *
import dwave_networkx as dnx
import numpy as np
import pickle
import networkx as nx
import scipy
import sys
import time

id = f"_{sys.argv[1]}_{sys.argv[2]}"
dim = 50
m=7
t=4
s = 9
k = 4
max_iter = 10
time_limit = 1800
thres = 500
G = dnx.zephyr_graph(m,t=t)
# print(nx.diameter(G),len(G.nodes()))
# exit(0)


# Q = BandWidthMatrix(dim, s)

# Generate a QP instance graph T with the avg degree inside the bound
# T has n*k nodes

bound = [0, 100]
maxTry = 100
while maxTry > 0:
    # T = nx.erdos_renyi_graph(40, 0.16)
    T = nx.random_regular_graph(8,36)
    # T = nx.barabasi_albert_graph(30,8)
    degree = 0
    for n in T.nodes():
        degree += k*k*T.degree(n)+2 *k -2
    avgDegree = degree / (k*len(T.nodes()))
    print(f'avgDegree: {avgDegree:.3}')
    if avgDegree>bound[0] and avgDegree<bound[1] and nx.is_connected(T):
        break
    maxTry-=1
if maxTry<=0:
    raise Exception("Cannot get a graph with the avg degree inside the bound")

def genCPPBench(H,G, paths, name='bench.cpp', reserve=None):
    Hstr = pyG2CppG(H, 'triangle')
    Gstr = pyG2CppG(G, 'square')
    towrite = '\n'.join(['#include "../include/find_embedding/find_embedding.hpp"' , Hstr, Gstr])

    for path in paths:
        with open(path+name, 'w') as f:
            f.write(towrite)
    if reserve:
        with open(reserve, 'w') as f:
            f.write(towrite)

def rewriteRun(path, id):
    with open(path+"example.cpp", 'r') as f:
        contents = f.read()
    contents = contents.replace(f'bench.cpp', f"data{id}.cpp")
    with open(path + f"example{id}.cpp", 'w') as f:
        f.write(contents)



# benchmark = "bench.npy"
# Q = np.load(benchmark)



Q = nx.adjacency_matrix(T).todense()

# for i in range(Q.shape[0]):
#     print(Q[i])
bt = np.random.rand(Q.shape[0])
model = QHD.QP(Q, bt)
model.dwave_setup(resolution=k, api_key='DEV-b9a33dfe7d8013b6e0358d696729673ab302e739', embedding_scheme='unary')
h,J = model.qhd_base.backend.calc_h_and_J()
H = list(J.keys())


# T = nx.random_regular_graph(m,n)
# H=T.edges()
with open('H.pkl', 'wb') as f:
    pickle.dump(H, f)

# G = dnx.pegasus_graph(m=10)
MaxL = max([max(a[0], a[1]) for a in H])
print(f"has {MaxL+1} logical qubits and {len(G.nodes())} physical qubits")
T = nx.Graph()
print("graph")
paths = ["optMinor/examples/", "baseMinor/examples/"]
genCPPBench(H,G.edges(),paths,reserve=f"data/data{id}.cpp")
for p in paths:
    rewriteRun(p, id)

if __name__ != '__main__':
    c_dis_l = []
    for e in H:
        T.add_edge(e[0], e[1])
    center = nx.center(T)

    for v in T.nodes():
        dis = min([nx.shortest_path_length(T,v,u) for u in center])
        c_dis_l.append((v,dis))
    c_dis = {v[0]: v[1] for v in c_dis_l}
if __name__ == '__main__':
    for e in H:
        T.add_edge(e[0], e[1])
    RG = nx.diameter(G)
    RH = nx.diameter(T)
    print(f"avg degree {2*len(T.edges()) / len(T.nodes())}, total edge: {len(T.edges())}")
    degree_list = list(range(MaxL))
    degree_list.sort(key=lambda v: T.degree(v),reverse=True)
    print(degree_list)
    degree={}
    print(f"H diameter: {RH}, G diameter: {RG}, recommended threshold: {(RG+1)//3}")
    # print("radius sort")
    # c_dis_l.sort(key=lambda a:a[1])
    # print(c_dis_l)
    # print([a[0] for a in c_dis_l])
    start = time.time()
    totalRun = 1
    good_it = 0
    totalCount = 0
    for i in range(totalRun):
        embed = find_embedding(H, G.edges(),timeout=5000, chainlength_patience=2)
        res = False if len(embed)==0 else True
        count = getCount(embed)
        if res:
            good_it += 1
            totalCount += count
        print(f'it: {i}, good_it: {good_it}, count: {count}, avg: {totalCount / good_it}')
    end = time.time()
    print(f"use {end-start}s")
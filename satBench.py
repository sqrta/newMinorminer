from qhdopt import QHD
from utils import *
import dwave_networkx as dnx
import numpy as np
import pickle
import networkx as nx
import scipy
import sys
from minorminer import find_embedding

# QP intances source
src = "sgenData/"
dir = "3_digit_clauses/"
id = sys.argv[1]
file = "sgen180-100"
# file = '9a296539e33398c9ae36663371a63b39-randomG-Mix-n17-d05N1357_E2236.edge'
file = 'b5c3e33e90f4c95502754c7e2e92a6d2-randomG-B-Mix-n16-d05N2108_E3675.edge'

# Hardware graph G
t=4
s = 9
k = 4
max_iter = 10
time_limit = 1800
thres = 500
m=15
G = dnx.zephyr_graph(m,t=t)
# G = dnx.pegasus_graph(20)


target = src + dir + file 
with open(target, 'r') as f:
    content = f.read()
data = eval(content)
print(len(data))

nameDict = {}
edges = []
for e in data:
    if e[0]==e[1]:
        continue
    if e[0] in nameDict.keys():
        u = nameDict[e[0]]
    else:
        u = len(nameDict.keys())
        nameDict[e[0]] = u
    if e[1] in nameDict.keys():
        v = nameDict[e[1]]
    else:
        v = len(nameDict.keys())
        nameDict[e[1]] = v
    edges.append((u,v))


dim = 50



# print(nx.diameter(G),len(G.nodes()))
# exit(0)


def genCPPBench(H,G, paths, name='bench.cpp', reserve=None, source=None):
    Hstr = pyG2CppG(H, 'triangle')
    Gstr = pyG2CppG(G, 'square')
    towrite = ""
    if source:
        towrite += "//" + source + "\n"
    towrite += '\n'.join(['#include "../include/find_embedding/find_embedding.hpp"' , Hstr, Gstr])

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
benchmark = "bench.npy"

# T = nx.barabasi_albert_graph(n,m)
# T = nx.random_regular_graph(m,n)
# H=T.edges()
source = 'sgen1-sat-140-100'
H = edges



MaxL = max([max(a[0], a[1]) for a in H])
print(f"has {MaxL+1} logical qubits and {len(G.nodes())} physical qubits")
T = nx.Graph()
print("graph")
paths = ["optMinor/examples/", "baseMinor/examples/"]
genCPPBench(H,G.edges(),paths,reserve=f"data/data{id}.cpp",source=file)
for p in paths:
    rewriteRun(p, id)

if __name__ == '__main__':
    for e in H:
        T.add_edge(e[0], e[1])
    print(f"avg degree {2*len(T.edges()) / len(T.nodes())}, total edge: {len(T.edges())}")
    RG = nx.diameter(G)
    RH = nx.diameter(T)

    
    degree_list = list(range(MaxL))
    # degree_list.sort(key=lambda v: T.degree(v),reverse=True)
    # print(degree_list)
    degree={}
    print(f"H diameter: {RH}, G diameter: {RG}, recommended threshold: {(RG+1)//3}")
    import time
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

    # print("radius sort")
    # c_dis_l.sort(key=lambda a:a[1])
    # print(c_dis_l)
    # print([a[0] for a in c_dis_l])

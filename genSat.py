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
m=11
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

def genCPPBench(G, paths, name='bench.cpp', reserve=None):
    # Hstr = pyG2CppG(H, 'triangle')
    with open('data/data_s_1.cpp', 'r') as f:
        contents = f.readlines()
    Hstr = contents[1]
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


print(f"has {len(G.nodes())} physical qubits")
# benchmark = "bench.npy"
# Q = np.load(benchmark)

paths = ["optMinor/examples/", "baseMinor/examples/"]
genCPPBench(G.edges(),paths,reserve=f"data/data{id}.cpp")
for p in paths:
    rewriteRun(p, id)

#!/bin/bash

python3 rewrite.py _$2_$3
cp ../../data/data_$2_$3.cpp ./
g++ example_$2_$3.cpp -std=c++17 -O2 -o example_$2_$3 -pthread
./example_$2_$3 $1 $2 $3

rm ./example_$2_$3 example_$2_$3.cpp data_$2_$3.cpp

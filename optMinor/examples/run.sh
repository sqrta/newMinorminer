#!/bin/bash

python3 rewrite.py _$3_$4
cp ../../data/data_$3_$4.cpp ./
g++ example_$3_$4.cpp -std=c++17 -O2 -o example_$3_$4 -pthread
./example_$3_$4 $1 $2 $3 $4

rm ./example_$3_$4 example_$3_$4.cpp data_$3_$4.cpp

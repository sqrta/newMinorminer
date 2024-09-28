// Copyright 2017 - 2020 D-Wave Systems Inc.
//
//    Licensed under the Apache License, Version 2.0 (the "License");
//    you may not use this file except in compliance with the License.
//    You may obtain a copy of the License at
//
//        http://www.apache.org/licenses/LICENSE-2.0
//
//    Unless required by applicable law or agreed to in writing, software
//    distributed under the License is distributed on an "AS IS" BASIS,
//    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//    See the License for the specific language governing permissions and
//    limitations under the License.

#include <iostream>
#include "bench.cpp"

#include <fstream>

using namespace std;
using namespace std::chrono;
using clockt = std::chrono::high_resolution_clock;

class MyCppInteractions : public find_embedding::LocalInteraction {
  public:
    bool _canceled = false;
    void cancel() { _canceled = true; }

  private:
    void displayOutputImpl(int, const std::string& mess) const override { std::cout << mess << std::endl; }
    void displayErrorImpl(int, const std::string& mess) const override { std::cerr << mess << std::endl; }
    bool cancelledImpl() const override { return _canceled; }
};

void printChain(vector<vector<int>> chains){
    for (auto chain : chains){
        printf("{");
        for (auto u: chain)
            printf("%d, ", u);
        printf("}, ");
    }
        
    printf("\n");
}

int main(int argc, char *argv[]) {
        srand(time(NULL));
    std::srand(std::time(0));
    auto start=clockt::now();
    find_embedding::optional_parameters params;
    params.localInteractionPtr.reset(new MyCppInteractions());
    params.timeout=3500;
    params.tries=10;
    int thres = atoi(argv[1]);
    params.thres=thres;
    params.initThresFlag=0;
    uint32_t x = time(NULL);
    params.rng.seed(x);
    int good_it = 0;
    int minCount = 999999;
    int max_it =atoi(argv[2]);
    string threadID(argv[3]);
    string dataID(argv[4]);
    vector<double> wrongDatas;
    double total = 0;
    double avg;
    ofstream file;
    cout << "threadId " << threadID << ", DataID " << dataID <<", timeout: " << params.timeout << " vars: " << triangle.num_nodes() << " machineNodes: "<< square.num_nodes() <<endl;
    for (int i = 0; i < max_it; i++)
    {
    auto local_start=clockt::now();
    int count=0;
    // printf("[");
    std::vector<std::vector<int>> chains;
    int res=0;
    int maxCount=10;
    res = find_embedding::findEmbedding(triangle, square, params, chains);
    while (!res && maxCount>0)
    {
        printf("res %d, maxCount: %d\n", res, maxCount);
        res = find_embedding::findEmbedding(triangle, square, params, chains);       
        maxCount -=1;
    }
    auto local_end = clockt::now();
    double duration = static_cast<double>(duration_cast<microseconds>(local_end - local_start).count()) / 1e6;
    if (duration>1000) wrongDatas.push_back(duration);
    if (res) {
        
        for (int u=0; u < chains.size(); u++) {
            auto chain = chains[u];
            count+=chain.size();
            // printf("{");
            // for (auto u:chain){
            //     printf("%d, ", u);
            // }
            // printf("}, ");
        }
        // printChain(chains);
        // printf("init map\n");
        // printChain(init);
        // if (count<530) 
        good_it+=1;
        if (count<minCount) minCount = count;
        total = total +(double)count;
        avg = total/(double)(good_it);
        printf("it: %d, count: %d, good_it: %d, min: %d, avg: %f, duration: %f\n", i, count, good_it, minCount, avg, duration);
        // printf("]\nit: %d, count: %d, min: %d, avg: %f\n", i, count, minCount, avg);
        
    } else {
        printf("it: %d fail, good_it: %d, min: %d\n", i, good_it, minCount);
    }

   }
   auto end = clockt::now();
    double duration = static_cast<double>(duration_cast<microseconds>(end - start).count()) / 1e6;
    for (auto u : wrongDatas){
        duration -= u;
        max_it -= 1;
    }
    printf("%d iterations use %fs\n", max_it,duration);
    printf("minCount: %d\n", minCount);
    file.open("thread"+threadID, std::ios_base::app);
    file << dataID << " goodit: " << good_it << " time: " << duration << "s for " << max_it << " iterations, avg: " << avg <<" thres: " << thres << " vars: " << triangle.num_nodes() << " machineNodes: "<< square.num_nodes() <<endl;
    return 0;
}

def rewriteRun(path, id):
    with open(path+"example.cpp", 'r') as f:
        contents = f.read()
    contents = contents.replace(f'bench.cpp', f"data{id}.cpp")
    with open(path + f"example{id}.cpp", 'w') as f:
        f.write(contents)

import sys
id = sys.argv[1]
rewriteRun("./", id)
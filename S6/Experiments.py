from functools import reduce
from os import system
import numpy as np
from sklearn.model_selection import ParameterGrid

if __name__ == '__main__':
    param_grid = {
        # ExtractData
        'minfreq': np.arange(0.0, 0.3, step=0.1, dtype=float).tolist(),
        'maxfreq': np.arange(0.4, 1.0, step=0.1, dtype=float).tolist(),
        'numwords': [100, 250],
        # GeneratePrototypes
        'nclust': np.arange(2, 10, dtype=int).tolist(),
        # MRKmeans
        'iter': np.arange(5, 30, step=5, dtype=int).tolist(),
        'nmaps': np.arange(2, 5, dtype=int).tolist(),
        'nreduces': np.arange(2, 5, dtype=int).tolist(),
        'sim': ['jaccard', 'cosine']
    }

    grid = ParameterGrid(param_grid)

    for params in grid:
        folder_name = reduce(lambda acc, x: f'{acc} {x[0]}_{x[1]}', params.items(), '')
        extract_data_params = f'--index arxivs --minfreq {params["minfreq"]} ' \
                              f'--maxfreq {params["maxfreq"]} --numwords {params["numwords"]}'
        system(f'python ExtractData.py {extract_data_params}')
        print(f'Data extracted for {extract_data_params}')

        prototype_params = f'--nclust {params["nclust"]}'
        system(f'python GeneratePrototypes.py {prototype_params}')
        print(f'Initial Prototypes generated for {prototype_params}')

        mr_kmeans_params = f'--iter {params["iter"]} --nmaps {params["nmaps"]} --nreduces {params["nreduces"]}' \
                           f'--folder {folder_name} --sim {params["sim"]}'
        system(f'python MRKmeans.py {mr_kmeans_params}')
        print(f'K-means calculated for {mr_kmeans_params}')

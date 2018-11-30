from os import system

import numpy as np

if __name__ == '__main__':
    # Extract data
    min_freq = np.arange(0.0, 0.3, step=0.1, dtype=float).tolist()
    max_freq = np.arange(0.5, 0.8, step=0.1, dtype=float).tolist()
    numwords = [100, 250]
    nclust = np.arange(2, 21, step=2, dtype=int).tolist()
    iterations = np.arange(5, 15, step=5, dtype=int).tolist()
    nmaps = np.arange(2, 6, dtype=int).tolist()
    nreduces = np.arange(2, 6, dtype=int).tolist()
    sim = ['jaccard']

    for minfreq in min_freq:
        for maxfreq in max_freq:
            for nw in numwords:
                folder_data_name = f'min_{minfreq}-max_{maxfreq}-n_{nw}'
                extract_data_params = f'--index news --minfreq {minfreq} --maxfreq {maxfreq} ' \
                                      f'--numwords {nw} --folder {folder_data_name}'
                system(f'python ExtractData.py {extract_data_params}')
                print(f'Data extracted for {extract_data_params}')
                for k in nclust:
                    folder_prot_name = f'{folder_data_name}/k_{k}'
                    prototype_params = f'--nclust {k} --folder {folder_prot_name}'
                    system(f'python GeneratePrototypes.py {prototype_params}')
                    print(f'Initial Prototypes generated for {prototype_params}')
                    for i in iterations:
                        for m in nmaps:
                            for r in nreduces:
                                for f in sim:
                                    folder_results_name = f'{folder_prot_name}/i_{i}-m_{m}-r_{r}-f_{f}'
                                    mr_kmeans_params = f'--iter {i} --nmaps {m} --nreduces {r} ' \
                                                       f'--folder {folder_results_name}'
                                system(f'python MRKmeans.py {mr_kmeans_params}')
                                print(f'K-means calculated for {mr_kmeans_params}')

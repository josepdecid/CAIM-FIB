import json

import numpy as np

from S3.Rocchio import Rocchio
from sklearn.model_selection import ParameterGrid

if __name__ == '__main__':
    rocchio = Rocchio()

    param_grid = {
        'alpha': np.arange(1, 50, 2),
        'beta': np.arange(1, 50, 2),
        'n_rounds': np.arange(1, 100, 10),
        'k': np.arange(5, 50, 5),
        'r': np.arange(2, 11),
        'query': [
            ['toronto', 'caim'],
            ['toronto^2', 'nyc'],
            ['toronto', 'vancouv^2'],
            ['doctor', 'student^8']
        ]
    }

    params = ParameterGrid(param_grid)

    experiments = []
    for p in params:
        print(p)
        rocchio.update_parameters(alpha=p['alpha'],
                                  beta=p['beta'],
                                  n_rounds=p['n_rounds'],
                                  k=int(p['k']),
                                  r=p['r'])
        results = rocchio.query('news', p['query'])
        experiments.append({
            'parameters': {
                'alpha': int(p['alpha']),
                'beta': int(p['beta']),
                'n_rounds': int(p['n_rounds']),
                'k': int(p['k']),
                'r': int(p['r']),
            }, 'results': results
        })

    with open('results.json', mode='w') as f:
        f.write(json.dumps(experiments))

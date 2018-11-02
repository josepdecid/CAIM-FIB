import json
from datetime import datetime

import numpy as np
from sklearn.model_selection import ParameterGrid

from S3.Rocchio import Rocchio

FILE_NAME = 'results.json'

if __name__ == '__main__':
    with open(FILE_NAME, mode='w') as f:
        f.write('[')

    rocchio = Rocchio()

    param_grid = {
        'alpha': np.arange(1, 9, 1),
        'beta': np.arange(1, 9, 1),
        'n_rounds': np.arange(1, 42, 10),
        'k': np.arange(5, 25, 5),
        'r': np.arange(2, 10, 2),
        'query': [
            ['toronto', 'caim'],
            ['toronto^2', 'nyc'],
            ['toronto', 'vancouv^2'],
            ['doctor', 'student^8']
        ]
    }

    params = ParameterGrid(param_grid)

    for p in params:
        p = {key: int(val) if key != 'query' else val for key, val in p.items()}
        print(str(datetime.now()) + ' ' + json.dumps(p))
        rocchio.update_parameters(alpha=p['alpha'],
                                  beta=p['beta'],
                                  n_rounds=p['n_rounds'],
                                  k=p['k'],
                                  r=p['r'])
        results = rocchio.query('news', p['query'])
        with open(FILE_NAME, mode='a') as f:
            f.write(json.dumps({
                'parameters': {
                    'alpha': p['alpha'],
                    'beta': p['beta'],
                    'n_rounds': p['n_rounds'],
                    'k': p['k'],
                    'r': p['r'],
                }, 'results': results
            }) + ',')

    with open(FILE_NAME, mode='a') as f:
        f.write(']')

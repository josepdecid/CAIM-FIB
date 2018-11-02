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
        'alpha': map(float, np.arange(0.1, 2, 0.05)),
        'beta': map(float, np.arange(0.1, 2, 0.05)),
        'n_rounds': map(int, np.arange(1, 20, 1)),
        'k': map(int, np.arange(1, 30, 3)),
        'r': map(int, np.arange(2, 10, 2)),
        'query': [
            ['toronto', 'caim'],
            ['toronto^2', 'nyc'],
            ['toronto', 'vancouv^2'],
            ['doctor', 'student^8']
        ]
    }

    params = ParameterGrid(param_grid)

    for p in params:
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

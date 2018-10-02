import os
import requests


if __name__ == '__main__':
    try:
        res = requests.get(os.environ.get(º))
        print(res.content)
    except Exception:
        print('Elastic search is not running')

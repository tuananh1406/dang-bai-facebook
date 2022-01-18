# coding: utf-8
import json
import requests


URL = "https://chothuesimcode.com/api"


def lay_thong_tin(api_key):
    param = dict(
        act='account',
        apik=api_key,
    )
    print(param)
    response = requests.get(
        URL,
        params=param,
    )
    ket_qua = json.loads(response.text)
    print(ket_qua['Result'])


if __name__ == '__main__':
    api_key = 'baa3554e8a575e20'
    lay_thong_tin(api_key)

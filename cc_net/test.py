from itertools import repeat
from operator import add

from submitit import Executor


def parse_doc():
    # hashes_files = repeat([])
    # for f in hashes_files:
    #     print(f)
        
    a = [1, 2, 3]
    b = [10, 20, 30]
    res = Executor.map_array(add, a, b)
    print(res)
    # headers = ['WARC/1.0', 
    #     'WARC-Type: conversion',
    #     'WARC-Target-URI: https://zw.lt/kultura-historia/wilno-zamienilo-sie-w-galerie-sztuki-pod-otwartym-niebem/', 
    #     'WARC-Date: 2023-03-20T09:53:29Z', 
    #     'WARC-Record-ID: <urn:uuid:0cc0ce8c-ba9b-49a2-a6e0-d93b2ea65766>', 
    #     'WARC-Refers-To: <urn:uuid:fc2f4e32-d5b8-45e7-b65f-f083c27237c9>', 
    #     'WARC-Block-Digest: sha1:IJDXNKVVS2DY7V5YHW7BJUBKY7TGMFBH', 
    #     'WARC-Identified-Content-Language: pol', 
    #     'Content-Type: text/plain', 
    #     'Content-Length: 2774', '']
    # headerDic = {}
    # for header in headers:
    #     if len(header.split()) >= 2:
    #         headerDic[header.split()[0]] = header.split()[1]
    # # print(headerDic)
    # url = ("WARC-Target-URI:" in headerDic) and headerDic["WARC-Target-URI:"] or ""
    # date = ("WARC-Date:" in headerDic) and headerDic["WARC-Date:"] or ""
    # digest = ("WARC-Block-Digest:" in headerDic) and headerDic["WARC-Block-Digest:"] or ""
    # length = ("Content-Length:" in headerDic) and headerDic["Content-Length:"] or 0
    # language = ("WARC-Identified-Content-Language:" in headerDic) and headerDic["WARC-Identified-Content-Language:"] or ""
    # print(f"url:{url} date: {date} digest: {digest} language: {language} ")

if __name__ == "__main__":
    parse_doc()
# Sample AIWolf Python agent using aiwolf package
Sample AIWolf agent written in Python using [aiwolf package](https://github.com/AIWolfSharp/aiwolf-python).
## Prerequisites
* Python 3.8
* [aiwolf package]((https://github.com/AIWolfSharp/aiwolf-python)). 

## インストール

- poetryとpipどちらでもよい
```
poetry install
```
or
```
pip install -r requirements.txt
```

## How to use
1. 先にjavaの環境を実行する(エージェントを一人余る状態にしておく)
2. pythonエージェントの起動

- pip 使っている場合
```
python start.py -h locahost -p 10000 -n name_you_like
```

- poetry 使っている場合
```
poetry run python3 start.py -h locahost -p 10000 -n name_you_like
```


※ localhostは自分のpcのipアドレス

`ipconfig`で確認できる

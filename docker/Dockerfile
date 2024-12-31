# ベースコンテナの指定(java18)
FROM openjdk:18-slim 

# baseのアップグレードとunzipとwgetのインストール 
RUN apt-get update && apt-get upgrade -y \
    && apt-get install  -y \
    && unzip \
    && wget

WORKDIR /usr/src
# /usr/src/にaiwolfのclientをインストール
RUN wget https://aiwolf.org/control-panel/wp-content/uploads/2023/06/aiwolf-ver0.6.4.zip \
    && unzip aiwolf-ver0.6.4.zip  

# AIWolf-ver0.6.4の実行ファイルがある場所を実行場所に指定
WORKDIR /usr/src/AIWolf-ver0.6.4
RUN sed -i '1s/$/ -j/' AutoStarter.sh \
    && 

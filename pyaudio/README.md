## インストール
```
$ pip install -r requirement.txt
$ pip install awscli
```

## 使い方
```
$ aws configure
AWS Access Key ID [None]: 自分のAK
AWS Secret Access Key [None]: 自分のSAK
Default region name [None]: ap-northeast-1
Default ouput format [None]: json
```

### 起動方法
1. server.pyの行20〜23、\<region\>と\<bucket\>と\<table\>の部分を自分の値に変更
2. コンソールからserver.pyを起動
2. 2.のコンソールとは別のコンソールから、client.pyを起動

### 終了方法
1. client.pyのコンソールでCtrl+Cで停止
2. server.pyが自動停止

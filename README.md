# bacnet-configurator
bacnet config file generator for thingsboard-gateway
--------
### 의존성 설치
```bash
$ python3 -m pip install requirements
```
--------
### 사용법
```bash
$ python3 bac_conf.py --ip_addr='your.ipv4.bacnet.addr' --subnet=24 --port=47808
```   
* ip_addr : string =  BACnet Interface의 IPV4 주소 
* subnet : integer = BACnet Interface network의 subnet mask 지정 기본 24
* port : integer = BACnet Interface의 통신 포트 기본 47808 
* output : bacnet.json 출력(thingsboard iot gateway 의 config 폴더에 넣고 사용)
------
```bash 
# this is beta
$ python3 converter.py --mapping_table=LUT.csv --config bacnet.json
```
### 구성도

### Limits
* 재귀탐색 미구현 : Root Gateway 밑 Gateway 에 또다른 하위 Gateway 가 물려 있을 경우 재귀 탐색하지 않음
------
### Dependencies
* BAC0==21.12.3
* bacpypes==0.18.6
* certifi==2022.5.18.1
* charset-normalizer==2.0.12
* colorama==0.4.4
* idna==3.3
* pytz==2022.1
* urllib3==1.26.9
* requests>=2.24.0


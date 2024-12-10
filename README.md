# DSG, Do Something Good

## Space with You, Worlty

![HACS][hacs-shield]
![Version v0.0.9][version-shield]

- [버전 기록정보](#version-history)
- [안내사항](#안내사항)
- [준비물](#준비물)
- [설치방법](#설치방법)
- [추가방법](#추가방법)

문의 : 월티 [홈페이지](https://worlty.com)

<br/>

## 버전 기록정보

| 버전  |    날짜    | 내용                           |
| :---: | :--------: | :----------------------------- |
| 0.0.9 | 2024.12.10 | minor fix                      |
| 0.0.8 | 2024.12.07 | minor fix                      |
| 0.0.7 | 2024.12.03 | minor fix                      |
| 0.0.6 | 2024.11.17 | minor fix                      |
| 0.0.5 | 2024.11.16 | minor fix                      |
| 0.0.4 | 2024.10.29 | 난방 관련 child 추가           |
| 0.0.3 | 2024.10.29 | minor fix                      |
| 0.0.2 | 2024.10.23 | 난방 타이머제어 관련 내용 추가 |
| 0.0.1 | 2024.10.14 | HA 업데이트 대응 및 child 추가 |
| 0.0.0 | 2024.09.01 | 서비스 공개                    |

<br/>

## 안내사항

- 지능형 홈네트워크의 모든 기능을 이용하려면 홈네트워크 장치 제조사 혹은 건설사의 `정식 서비스를 이용`하시기 바랍니다.
- 본 서비스는 `스마트홈 기기제어 프로토콜`인 `KSX4506`을 지원합니다.

<br/>

## 준비물

- Home Assistant (최신버전)
- 지능형 홈네트워크가 설치되어 있는 주거공간
- `아파트 시공상황에 따라서 지원되는 항목이 다를 수 있습니다.`

### 비밀번호(Access Token) 발급 방법

- 월티 앱 실행
  ![worlty_token_01](/img/worlty_token_01.jpg)
  <br/>

- 메뉴 클릭 > 내 장치 목록
  ![worlty_token_02](/img/worlty_token_02.jpg)
  <br/>

- 장치 클릭
  ![worlty_token_03](/img/worlty_token_03.jpg)
  <br/>

- 토큰 발급하기
  ![worlty_token_04](/img/worlty_token_04.jpg)
  <br/>

- 최대 연결 개수, 포트 설정 후 발급하기 클릭
  ![worlty_token_05](/img/worlty_token_05.jpg)
  <br/>

- 비밀번호(Access Token) 확인
  ![worlty_token_06](/img/worlty_token_06.jpg)

<br/>

## 설치방법

## 월티 통합구성요소를 HA에 설치하는 방법

### HACS

- HACS > 우측상단 메뉴 > `Custom repositories` 선택
- `Repository`에 `https://github.com/GuGu927/worlty_homeassistant` 입력
- `Type`에 `Integration` 선택 후 `ADD` 클릭
- HACS 에서 `Worlty`를 찾아서 설치
- HomeAssistant 재시작

<br/>

### 수동설치

- `https://github.com/GuGu927/worlty_homeassistant` 페이지에서 `Code/Download ZIP` 을 눌러 파일을 다운로드, 내부의 `custom_components/worlty` 폴더 확인
- HomeAssistant 설정폴더인 `/config` 내부에 `custom_components` 폴더를 생성(이미 있으면 다음 단계)<br/>설정폴더는 `configuration.yaml` 파일이 있는 폴더를 의미합니다.<br>
- `/config/custom_components`에 위에서 다운받은 `worlty` 폴더를 넣기<br>
- HomeAssistant 재시작

<br/>

## 추가방법

## 월티 패드를 HomeAssistant에 추가하는 방법

### Discovery(**권장**)

- HomeAssistant 사이드패널 > 알림 > New devices discovered > 발견된 `Worlty` 혹은 `월티` 구성하기<br>
- HomeAssistant 사이드패널 > 설정 > 기기 및 서비스 > 통합 구성요소 > 발견된 `Worlty` 혹은 `월티` 구성하기<br>
- 앱에서 발급받은 `비밀번호(Access Token)`를 입력.<br>
- 완료!
- `같은 네트워크 내에 존재하는 장치만 자동으로 검색됩니다.`

<br/>

### 통합구성요소 추가

- HomeAssistant 사이드패널 > 설정 > 기기 및 서비스 > 통합구성요소 > 통합구성요소 추가하기<br>
- 검색창에서 `Worlty` 혹은 `월티` 입력 후 선택<br>
- IP에 추가할 `월티 장치의 IP주소`, 앱에서 설정한 `포트`, 앱에서 발급받은 `비밀번호(Access Token)`를 입력.

[version-shield]: https://img.shields.io/badge/version-v0.0.9-orange.svg
[hacs-shield]: https://img.shields.io/badge/HACS-Custom-red.svg

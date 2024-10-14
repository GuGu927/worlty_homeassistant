# DSG, Do Something Good

## Space with You, Worlty

![HACS][hacs-shield]
![Version v0.0.1][version-shield]

- [버전 기록정보](#version-history)
- [주의사항](#주의사항)
- [준비물](#준비물)

문의 : 월티 [홈페이지](https://worlty.com)

<br/>

## 버전 기록정보

| 버전  |    날짜    |              내용              |
| :---: | :--------: | :----------------------------: |
| 0.0.0 | 2024.03.02 |          서비스 공개           |
| 0.0.1 | 2024.10.14 | HA 업데이트 대응 및 child 추가 |

## 주의사항

- 지능형 홈네트워크의 모든 기능을 이용하려면 홈네트워크 장치 제조사 혹은 건설사의 `정식 서비스를 이용`하시기 바랍니다.
- 본 서비스는 `스마트홈 기기제어 프로토콜`인 `KSX4506`을 지원합니다.

<br/>

## 준비물

- 지능형 홈네트워크가 설치되어 있는 주거공간
- `시공상황에 따라서 지원되는 항목이 다를 수 있습니다.`

## 사용자 구성요소를 HA에 설치하는 방법

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

## 월티를 discovery로 추가하는 방법(**권장**)

### Discovery

- HomeAssistant 사이드패널 > 설정 > 통합 구성요소 > 발견된 `담다 어웨어` 구성하기<br>
- 완료!

## 월티를 통합구성요소로 설치하는 방법

### 통합구성요소

- HomeAssistant 사이드패널 > 설정 > 기기 및 서비스 > 통합구성요소 > 통합구성요소 추가하기<br>
- 검색창에서 `Worlty` 혹은 `월티` 입력 후 선택<br>
- IP에 추가할 `월티 장치의 IP주소`, 앱에서 설정한 `포트`, 앱에서 발급받은 `비밀번호(Access Token)`를 입력.

[version-shield]: https://img.shields.io/badge/version-v0.0.1-orange.svg
[hacs-shield]: https://img.shields.io/badge/HACS-Custom-red.svg

# VARCO TTS Generator
NC VARCO API 를 사용하여 엑셀 파일의 대사를 음성 파일(.wav)로 생성하는 도구입니다. 성우별 폴더 자동 생성 및 중복 파일 처리 기능을 지원합니다.

## 개발 환경
* Python Version: 3.12.6
* OS: Windows 10/11

## 설정
실행 전, 프로젝트 루트 경로에 `.env` 파일을 생성하고 아래 내용을 입력해야 합니다.
```
# NC VARCO API 인증 키
API_KEY="api_key"

# 대사 스크립트 엑셀 파일명(확장자 포함)
EXCEL_FILE="excel_file_name"

# (참고용) 보이스 리스트 조회 API 주소
VOICE_URL="voice list api url"

# 음성 생성 API 주소
GEN_URL="text to speech api url"

# 기본 실행 모드 (1: 전체 재생성, 2: 중복 건너뛰기(디폴트))
MODE="mode number(integer)"
```

## 사용 방법
### 0. 사전 작업
1. 엑셀 파일이 존재하고 양식이 동일한지 확인
2. `.env` 파일이 존재하고 양식이 동일한지 확인
3. 모드 번호 확인 `(1: 전체 재생성, 2: 중복 건너뛰기(디폴트))`

### 1. Python 스크립트로 실행
1. python 3.12.6 설치
2. 필수 라이브러리 설치
```
python -m pip install -r version_requirements.txt
```
3. 실행
```
python [file_name].py
```

### 2. exe 파일 실행
1. exe 파일 실행
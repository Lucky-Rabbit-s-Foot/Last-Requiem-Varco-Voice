import requests
import pandas as pd
import json
from dotenv import load_dotenv
import os

# ---------------------------------------------------
# [설정] .env 로드 및 환경 변수
# ---------------------------------------------------
load_dotenv()
       
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    print("오류: API_KEY 를 찾을 수 없습니다.")
    print("같은 디렉토리에 .env 파일이 존재하는지, API_KEY 가 입력되어 있는지 확인해주세요")
    exit()

URL = os.getenv("VOICE_URL")
if not URL:
    print("오류: URL 을 찾을 수 없습니다.")
    print("같은 디렉토리에 .env 파일이 존재하는지, VOICE_URL 가 입력되어 있는지 확인해주세요")
    exit()


# ---------------------------------------------------
# api 호출
# ---------------------------------------------------
def save_voice_list():
    # api 호출을 위한 request header
    headers = {
        "accept": "application/json",
        "openapi_key": API_KEY
    }
    
    try:
        # ---------------------------------------------------
        # 데이터 요청
        # ---------------------------------------------------
        print(f"데이터 요청 시작 ({URL})")
        response = requests.get(URL, headers=headers)
        
        if response.status_code != 200:
            print(f"요청 실패 (Code: {response.status_code})")
            print("""
                << 해결되지 않으면 번호와 함께 연락 바람 >>
                400번대 : 클라이언트 오류
                - 400: 잘못된 요청 (URL 확인)
                - 401: 인증 실패 (API_KEY 확인)
                - 403: 권한 없음 (API_KEY 확인)
                - 404: 페이지 없음 (URL 확인)
                - 429: 요청 과다 (잠시 대기 후 다시 요청)
                500번대 : 서버 오류
            """)
            return

        data = response.json()
        #print(data)

        # ---------------------------------------------------
        # 데이터 리스트 추출
        # ---------------------------------------------------
        print("데이터 요청 성공: 리스트 추출 시작")
        if isinstance(data, dict) and 'data' in data:
            voice_list = data['data']
        elif isinstance(data, list):
            voice_list = data
        else:
            voice_list = []
        print(f"리스트 추출 성공: 총 {len(voice_list)}개의 목소리 데이터를 가져왔습니다.\n")

        summary_data = []
        for i, v in enumerate(voice_list):
            # 1. 키 매핑
            s_uuid = v.get('speaker_uuid')
            s_name = v.get('speaker_name')
            desc = v.get('description') or ""
            
            # 2. 특징 추출
            emotion = s_name.split('(')[1].replace(')', '').strip() if '(' in s_name else ""
            tags = [t.strip() for t in desc.split(',')]
            if len(tags) != 5:
                print(f"{i}번째 데이터 description 예외 처리(데이터 확인 바람)")
                print(f"{i}-description: {desc}")
                continue
                
            # 3. 리스트에 추가
            summary_data.append({
                "이름": s_name,
                "감정": emotion,
                "성별": tags[0],
                "나이": tags[1],
                "음역대": tags[2],
                "음색": tags[3],
                "분위기": tags[4], 
                "UUID (코드)": s_uuid
            })

        # ---------------------------------------------------
        # 파일 저장
        # ---------------------------------------------------
        # 1. 엑셀로 저장
        excel_name = "varco_voices_list.xlsx"
        if os.path.exists(excel_name):
            try:
                os.remove(excel_name)
                print(f"기존 엑셀 파일 삭제: {excel_name}")
            except PermissionError:
                print("오류: 엑셀 파일을 삭제할 수 없습니다. 파일이 열려있는지 확인바랍니다.")
                return

        if summary_data:
            df = pd.DataFrame(summary_data)
            df.to_excel(excel_name, index=False)
            print(f"엑셀 저장 완료: {excel_name}")

        # 2. JSON으로 저장 (들여쓰기 사용)
        json_name = "varco_voices.json"
        if os.path.exists(json_name):
            try:
                os.remove(json_name)
                print(f"기존 json 파일 삭제: {json_name}")
            except PermissionError:
                print("오류: json 파일을 삭제할 수 없습니다. 파일이 열려있는지 확인바랍니다.")
                return
        
        if summary_data:
            with open(json_name, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=4, ensure_ascii=False)
            print(f"json 저장 완료: {json_name}")
        
        print("\n모든 작업 완료")

    except Exception as e:
        print(f"에러 발생: {e}")

if __name__ == "__main__":
    save_voice_list()
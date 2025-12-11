import requests
import pandas as pd
import json
import argparse
from dotenv import load_dotenv
import os

# ==========================================
# [설정] API 키 입력
# ==========================================
load_dotenv()

API_KEY = os.getenv("API_KEY")
URL = os.getenv("VOICE_URL")

if not API_KEY or not URL:
    print("❌ 오류: .env 파일에서 API_KEY 을 찾을 수 없습니다.")
    print("   .env 파일이 같은 폴더에 있는지, 변수명이 정확한지 확인해주세요.")
    exit()


def save_voice_list():
    headers = {
        "accept": "application/json",
        "openapi_key": API_KEY
    }

    print(f"📡 데이터 요청 중... ({URL})")
    
    try:
        response = requests.get(URL, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ 요청 실패 (Code: {response.status_code})")
            return

        data = response.json()
        
        # 데이터 리스트 추출
        if isinstance(data, dict) and 'data' in data:
            voice_list = data['data']
        elif isinstance(data, list):
            voice_list = data
        else:
            voice_list = []

        print(f"✅ 총 {len(voice_list)}개의 목소리 데이터를 가져왔습니다.\n")

        # ---------------------------------------------------
        # 데이터 정리 및 가공
        # ---------------------------------------------------
        summary_data = []

        for v in voice_list:
            # 1. 키 매핑 (찾아낸 실제 키 이름 사용)
            s_uuid = v.get('speaker_uuid')
            s_name = v.get('speaker_name')
            desc = v.get('description') or ""  # None일 경우 빈 문자열 처리
            
            # 2. (옵션) 설명 텍스트에서 '성별' 자동 추출
            gender = "알수없음"
            if "남성" in desc:
                gender = "남성"
            elif "여성" in desc:
                gender = "여성"
            elif "아동" in desc: # 경우에 따라 추가
                gender = "아동"

            # 3. 리스트에 추가
            summary_data.append({
                "이름": s_name,
                "성별": gender,
                "설명": desc,
                "UUID (코드)": s_uuid
            })

        # ---------------------------------------------------
        # 파일 저장
        # ---------------------------------------------------
        
        # 1. 엑셀로 저장 (보기 편함)
        if summary_data:
            df = pd.DataFrame(summary_data)
            # 엑셀 파일명
            excel_name = "varco_voices_list.xlsx"
            df.to_excel(excel_name, index=False)
            print(f"💾 [엑셀 저장 완료] {excel_name}")

        # 2. JSON으로 저장 (게임 엔진 로드용)
        # 들여쓰기를 해서 가독성을 높여 저장합니다.
        json_name = "varco_voices.json"
        with open(json_name, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=4, ensure_ascii=False)
        print(f"💾 [JSON 저장 완료] {json_name}")
        
        print("\n✅ 모든 작업이 완료되었습니다! 폴더를 확인해주세요.")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")

if __name__ == "__main__":
    save_voice_list()
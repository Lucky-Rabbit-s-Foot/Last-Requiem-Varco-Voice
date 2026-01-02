import pandas as pd
import json
import os

# ==========================================
# [설정] 파일 이름
# ==========================================
JSON_FILE = "voice_data_full.json"  # 읽어올 JSON 파일명
EXCEL_FILE = "speakers.xlsx"     # 저장할 엑셀 파일명

def convert_json_to_excel():
    # 1. JSON 파일 읽기
    if not os.path.exists(JSON_FILE):
        print(f"❌ '{JSON_FILE}' 파일을 찾을 수 없습니다.")
        # 테스트를 위해 코드가 멈추지 않도록 샘플 데이터를 사용합니다 (파일이 없을 경우)
        print("   (샘플 데이터로 진행합니다...)")
        data = [
            {"speaker_uuid": "...", "speaker_name": "데리온(분노)", "saas_name": None, "description": "..."},
            {"speaker_uuid": "...", "speaker_name": "실라린(분노)", "saas_name": None, "description": "..."},
            {"speaker_uuid": "...", "speaker_name": "실라린(행복)", "saas_name": None, "description": "..."}
        ]
    else:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

    # 2. 데이터프레임(표)으로 변환
    df = pd.DataFrame(data)

    # -------------------------------------------------------
    # ✅ [핵심] 원하는 컬럼만 순서대로 선택하기
    # -------------------------------------------------------
    # JSON에 있는 키 이름 그대로 적어주세요.
    target_columns = ["speaker_name", "saas_name"]
    
    # 해당 컬럼만 뽑아내기 (없는 컬럼이 있으면 에러 방지를 위해 교집합 사용)
    available_cols = [c for c in target_columns if c in df.columns]
    df_filtered = df[available_cols]

    # (선택사항) 'null' 값을 진짜 텍스트 "null"로 보이게 하려면 주석 해제하세요.
    # df_filtered = df_filtered.fillna("null") 

    # 3. 엑셀로 저장
    try:
        df_filtered.to_excel(EXCEL_FILE, index=False) # index=False: 0,1,2... 숫자 행 번호 제외
        print(f"💾 엑셀 변환 완료! '{EXCEL_FILE}' 파일을 확인하세요.")
        print(f"   - 포함된 컬럼: {available_cols}")
    except PermissionError:
        print(f"❌ 오류: '{EXCEL_FILE}' 파일이 열려있습니다. 엑셀을 닫고 다시 실행해주세요.")

if __name__ == "__main__":
    convert_json_to_excel()
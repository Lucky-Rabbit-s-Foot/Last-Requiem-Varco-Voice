import requests
import pandas as pd
import os
import time
import base64
import argparse  # ✅ 매개변수 처리를 위한 라이브러리
from dotenv import load_dotenv

# ==========================================
# [설정] .env 로드 및 환경 변수
# ==========================================
load_dotenv()

API_KEY = os.getenv("API_KEY")
EXCEL_FILE = os.getenv("EXCEL_FILE")
URL = os.getenv("GEN_URL") 

SHEET_NAME = "scripts"
OUTPUT_DIR = "voicefiles"

# [보안 체크]
if not API_KEY or not EXCEL_FILE or not URL:
    print("❌ 오류: .env 파일에서 환경변수를 찾을 수 없습니다.")
    exit()

def get_unique_filename(directory, filename):
    """
    파일이 존재할 경우 _1, _2 접미사를 붙여 중복되지 않는 파일명을 반환
    """
    name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{name}_{counter}{ext}"
        counter += 1
    
    return new_filename

def run_batch_tts(mode):
    """
    mode: 1 (재생성/중복시 이름변경), 2 (건너뛰기)
    """
    # 1. 엑셀 파일 읽기
    if not os.path.exists(EXCEL_FILE):
        print(f"❌ '{EXCEL_FILE}' 파일이 없습니다.")
        return

    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
        df.fillna({'speed': 0, 'pitch': 0, 'text': '', 'voice': '', 'filename': 'temp'}, inplace=True)
    except Exception as e:
        print(f"❌ 엑셀 읽기 실패: {e}")
        return

    # 2. 폴더 생성
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"📂 '{OUTPUT_DIR}' 디렉터리를 생성했습니다.")

    # 모드 안내 출력
    mode_desc = "모든 파일 재생성 (중복 시 번호 부여)" if mode == 1 else "이미 있는 파일 건너뛰기"
    print(f"⚙️ 실행 모드: [{mode}] {mode_desc}")
    print(f"🚀 총 {len(df)}개의 대사를 처리합니다...\n")

    headers = {
        "Content-Type": "application/json",
        "openapi_key": API_KEY
    }

    success_count = 0
    
    for index, row in df.iterrows():
        original_fname = str(row['filename']).strip()
        text = str(row['text']).strip()
        voice_uuid = str(row['voice']).strip()
        speed = float(row['speed'])
        pitch = float(row['pitch'])

        if not text or not voice_uuid:
            continue

        if not original_fname.lower().endswith('.wav'):
            original_fname += '.wav'
        
        # -------------------------------------------------------
        # 모드에 따른 로직 분기
        # -------------------------------------------------------
        final_fname = original_fname
        save_path = os.path.join(OUTPUT_DIR, final_fname)
        
        if os.path.exists(save_path):
            if mode == 2:
                # 모드 2: 건너뛰기
                print(f"⏭️ [Skip] 이미 존재함: {final_fname}")
                continue 
            
            elif mode == 1:
                # 모드 1: 이름 변경하여 생성
                final_fname = get_unique_filename(OUTPUT_DIR, original_fname)
                save_path = os.path.join(OUTPUT_DIR, final_fname)

        # -------------------------------------------------------
        
        # API 요청 Payload
        payload = {
            "voice": voice_uuid,
            "text": text,
            "properties": {
                "speed": speed,
                "pitch": pitch
            }
        }

        print(f"[{index+1}/{len(df)}] 생성 중: {final_fname} (Voice: {voice_uuid[:8]}...)")

        try:
            response = requests.post(URL, headers=headers, json=payload)

            if response.status_code == 200:
                res_data = response.json()
                if 'audio' in res_data:
                    audio_bytes = base64.b64decode(res_data['audio'])
                    with open(save_path, "wb") as f:
                        f.write(audio_bytes)
                    print(f"  ✅ 저장 완료: {save_path}")
                    success_count += 1
                else:
                    print("  ⚠️ 응답에 'audio' 데이터가 없습니다.")
            else:
                print(f"  ❌ 실패 (Code: {response.status_code})")
                print(f"     메시지: {response.text}")

        except Exception as e:
            print(f"  ❌ 에러 발생: {e}")

        time.sleep(0.2)

    print(f"\n🎉 작업 종료! 총 {success_count}개의 파일이 처리되었습니다.")

if __name__ == "__main__":
    # ✅ 여기서 매개변수(Argument)를 설정합니다.
    parser = argparse.ArgumentParser(description="TTS 일괄 생성기")
    
    # -m 또는 --mode 옵션 추가 (기본값은 2)
    parser.add_argument(
        "-m", "--mode", 
        type=int, 
        default=2, 
        choices=[1, 2],
        help="생성 모드 설정 (1: 전체 재생성/중복시 이름변경, 2: 이미 있으면 건너뛰기)"
    )
    
    args = parser.parse_args()
    
    # 입력받은 모드로 함수 실행
    run_batch_tts(args.mode)
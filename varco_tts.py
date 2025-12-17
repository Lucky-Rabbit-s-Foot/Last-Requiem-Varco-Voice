import requests
import pandas as pd
import os
import time
import base64
from dotenv import load_dotenv
import time

# ==========================================
# [설정] .env 로드 및 환경 변수
# ==========================================
load_dotenv()

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    print("오류: API_KEY 를 찾을 수 없습니다.")
    print("같은 디렉토리에 .env 파일이 존재하는지, API_KEY 가 입력되어 있는지 확인해주세요")
    exit()

URL = os.getenv("GEN_URL")
if not URL:
    print("오류: URL 을 찾을 수 없습니다.")
    print("같은 디렉토리에 .env 파일이 존재하는지, GEN_URL 가 입력되어 있는지 확인해주세요")
    exit()

EXCEL_FILE = os.getenv("EXCEL_FILE")
if not EXCEL_FILE:
    print("오류: 엑셀파일 을 찾을 수 없습니다.")
    print("같은 디렉토리에 .env 파일이 존재하는지, EXCEL_FILE 가 입력되어 있는지 확인해주세요")
    exit()

EXE_MODE = int(os.getenv("MODE"))

SHEET_NAME = "scripts"
OUTPUT_DIR = "voicefiles"

# ---------------------------------------------------
# 중복 가능하도록 파일을 생성할 때
# 파일이 존재할 경우 _1, _2 접미사를 붙여 파일을 추가 생성
# ---------------------------------------------------
def get_unique_filename(directory, filename):
    name, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{name}_{counter}{ext}"
        counter += 1
    
    return new_filename

# ---------------------------------------------------
# 범위가 제한된 수 사용 시
# ---------------------------------------------------
def clamp(val, min, max):
    if val < min:
        return min
    elif val > max:
        return max
    else:
        return val

# ---------------------------------------------------
# mode: 1 (재생성/중복시 이름변경), 2 (건너뛰기)
# ---------------------------------------------------
def run_batch_tts(mode):
    # ---------------------------------------------------
    # 1. 엑셀 읽기
    # ---------------------------------------------------
    if not os.path.exists(EXCEL_FILE):
        print(f"오류: '{EXCEL_FILE}' 파일이 없습니다.")
        return

    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
        df.fillna({
            'speed': 1.3, 
            'pitch': 1, 
            'text': 'None', 
            'voice': 'None', 
            'filename': 'None', 
            'n_fm_steps': 8, 
            'seed': -1
            }, inplace=True)
    except Exception as e:
        print(f"오류: 엑셀 읽기 실패: {e}")
        return

    # ---------------------------------------------------
    # 2. 폴더 생성
    # ---------------------------------------------------
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"'{OUTPUT_DIR}' 디렉터리를 생성했습니다.")

    # ---------------------------------------------------
    # 모드 안내 출력
    # ---------------------------------------------------
    mode_desc = "모든 파일 재생성(중복 시 번호 부여)" if mode == 1 else "이미 있는 파일 건너뛰기"
    print(f"실행 모드: [{mode}] {mode_desc}")
    print(f"총 {len(df)}개의 대사를 처리합니다\n")

    # ---------------------------------------------------
    # api 호출
    # ---------------------------------------------------
    headers = {
        "Content-Type": "application/json",
        "openapi_key": API_KEY
    }

    success_count = 0

    for index, row in df.iterrows():
        start = time.time()
        # 1. 키 매핑
        original_fname = str(row['filename']).strip()
        text = str(row['text']).strip()
        speaker = str(row['voice']).strip() # name / uuid
        speed = float(row['speed'])
        pitch = float(row['pitch'])
        n_fm_steps = float(row['n_fm_steps'])
        seed = float(row['seed'])

        n_fm_steps = clamp(n_fm_steps, 8, 20)

        if not original_fname or not text or not speaker:
            print(f"{index} 번째 행 빈 칸 존재: 파일 이름 / 대사 / 성우 확인 바람")
            continue

        speaker_dir = os.path.join(OUTPUT_DIR, speaker)
        if not os.path.exists(speaker_dir):
            os.makedirs(speaker_dir)
            print(f"새 성우 폴더 생성: {speaker}")

        if not original_fname.lower().endswith('.wav'):
            original_fname += '.wav'
        
        # -------------------------------------------------------
        # 모드에 따른 로직 분기
        # -------------------------------------------------------
        final_fname = original_fname
        save_path = os.path.join(speaker_dir, final_fname)
        
        if os.path.exists(save_path):
            if mode == 2:
                # 모드 2: 건너뛰기
                print(f"이미 존재하는 파일 스킵: {speaker}/{final_fname}")
                continue 
            
            elif mode == 1:
                # 모드 1: 이름 변경하여 생성
                final_fname = get_unique_filename(speaker_dir, original_fname)
                save_path = os.path.join(speaker_dir, final_fname)

        
        # API 요청 Payload
        payload = {
            "voice": speaker,
            "text": text,
            "n_fm_steps": n_fm_steps,
            "seed": seed,
            "properties": {
                "speed": speed,
                "pitch": pitch
            }
        }

        print(f"[{index+1}/{len(df)}] 생성 중: {final_fname} (Voice: {speaker}...)")

        try:
            response = requests.post(URL, headers=headers, json=payload)

            if response.status_code == 200:
                res_data = response.json()
                if 'audio' in res_data:
                    audio_bytes = base64.b64decode(res_data['audio'])
                    with open(save_path, "wb") as f:
                        f.write(audio_bytes)
                    print(f"저장 완료: {save_path}")
                    success_count += 1
                else:
                    print("응답에 'audio' 데이터가 없습니다.")
            else:
                print(f"실패 (Code: {response.status_code})")
                print(f"메시지: {response.text}")

        except Exception as e:
            print(f"에러 발생: {e}")
        
        end = time.time()
        print(f"{index} 번째 소요 시간 : {end-start:.4f} 초")
        # 요청 과다 방지
        time.sleep(0.2)

    print(f"\n작업 종료! 총 {success_count}개의 파일이 처리되었습니다.")

if __name__ == "__main__":
    total_start = time.time()
    run_batch_tts(EXE_MODE)
    total_end = time.time()
    print(f"\n프로그램 종료 : {total_end - total_start:.4f} 초")
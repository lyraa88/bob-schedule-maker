import pandas as pd
import os

def load_data(path):
    # 파일이 없는 경우 빈 데이터프레임 생성 및 저장
    if not os.path.exists(path):
        df = pd.DataFrame(columns=["name", "password", "date"])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # 저장 시 인코딩 설정을 추가하여 한글 깨짐 방지
        df.to_csv(path, index=False, encoding='utf-8-sig')
    
    # [핵심 수정] 읽어올 때 password 컬럼을 무조건 문자열(str)로 읽도록 지정
    # 이렇게 하면 '0000'이 숫자 0으로 변하는 것을 막을 수 있습니다.
    return pd.read_csv(path, dtype={'password': str})

def save_schedule(path, name, password, selected_dates, meal_prefs=None):
    df = load_data(path)
    
    # 기존 해당 유저 데이터 삭제
    df = df[df['name'] != name]
    
    # 비밀번호를 4자리 문자열로 강제 고정 (앞에 0이 있으면 채워줌)
    # 예: 0 -> "0000", 123 -> "0123"
    safe_password = str(password).zfill(4)
    
    if not selected_dates:
        # 신규 등록 시
        new_row = pd.DataFrame([{"name": name, "password": safe_password, "date": None}])
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        # 일정 저장 시 날짜별 레코드 생성
        new_records = [{"name": name, "password": safe_password, "date": d} for d in selected_dates]
        df = pd.concat([df, pd.DataFrame(new_records)], ignore_index=True)
    
    # [핵심 수정] 저장 시에도 인코딩과 모든 컬럼의 형식을 유지
    df.to_csv(path, index=False, encoding='utf-8-sig')
import pandas as pd
import os

def load_data(path):
    if not os.path.exists(path):
        df = pd.DataFrame(columns=["name", "password", "date"])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_csv(path, index=False)
    return pd.read_csv(path)

def save_schedule(path, name, password, selected_dates, meal_prefs=None):
    df = load_data(path)
    # 기존 데이터 삭제
    df = df[df['name'] != name]
    
    if not selected_dates:
        # 신규 등록 시 유저 정보만 저장
        new_row = pd.DataFrame([{"name": name, "password": str(password), "date": None}])
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        # 일정 저장 시 날짜별 레코드 생성
        new_records = [{"name": name, "password": str(password), "date": d} for d in selected_dates]
        df = pd.concat([df, pd.DataFrame(new_records)], ignore_index=True)
    
    df.to_csv(path, index=False)
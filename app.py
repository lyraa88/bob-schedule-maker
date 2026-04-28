import streamlit as st
import pandas as pd
from datetime import datetime
import calendar
from dotenv import load_dotenv
import os
import sys

# 경로 및 환경설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.data_handler import load_data, save_schedule

load_dotenv()
DB_PATH = os.getenv("DB_PATH", "data/schedule.csv")
calendar.setfirstweekday(calendar.SUNDAY)

# 페이지 설정
st.set_page_config(page_title="BOB's schedule maker", layout="wide")

# --- 1. 라이트 모드 고정 및 UI 디자인 CSS ---
st.markdown("""
    <style>
    .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    .main-title {
        text-align: center;
        padding: 20px;
        background-color: #FF4B4B;
        color: white !important;
        border-radius: 15px;
        margin-bottom: 30px;
        font-family: 'Arial Black', sans-serif;
    }
    div[data-baseweb="input"] {
        background-color: #F0F2F6 !important; 
        border: 1px solid #E0E0E0 !important;
        border-radius: 8px !important;
    }
    input {
        color: #000000 !important; 
        -webkit-text-fill-color: #000000 !important;
    }
    div[data-testid="stWidgetLabel"] p {
        color: #333333 !important;
        font-weight: 500 !important;
    }
    div[role="tooltip"] {
        background-color: #E3F2FD !important; 
        color: #01579B !important;           
        border: 1px solid #BBDEFB !important;
        padding: 8px 12px !important;
        border-radius: 5px !important;
    }
    button[kind="primary"] {
        background-color: #FF0000 !important; 
        color: #FFFFFF !important;           
        border: none !important;
        font-weight: bold !important;
    }
    button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #EEEEEE !important;
    }
    .section-card {
        background-color: #F8F9FB !important;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #E6E9EF;
        margin-bottom: 15px;
        text-align: center;
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 최상단 서비스 제목
st.markdown("<div class='main-title'><h1>📅 BOB's schedule maker</h1></div>", unsafe_allow_html=True)

# 세션 상태 초기화
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'selected_dates' not in st.session_state:
    st.session_state.selected_dates = set()

# --- 2. 데이터 로드 및 집계 로직 ---
df = load_data(DB_PATH)
today = datetime.now()
year, month = today.year, today.month

# 참여 데이터 집계
active = df[df['date'].notna() & (df['date'] != "")]
if not active.empty:
    count_dict = active.groupby('date').size().to_dict()
    names_dict = active.groupby('date')['name'].apply(lambda x: ", ".join(x.unique())).to_dict()
    max_count = max(count_dict.values())
else:
    count_dict, names_dict, max_count = {}, {}, 0

# --- 3. 메인 레이아웃 ---
tab_main, tab_admin = st.tabs(["🗓️ 일정 관리", "⚙️ 관리자"])

with tab_main:
    col_left, col_right = st.columns([1, 2.5])

    with col_left:
        st.markdown("<div class='section-card'><h3>🔑 접속 및 등록</h3></div>", unsafe_allow_html=True)
        sub_tab1, sub_tab2 = st.tabs(["로그인", "신규 등록"])
        
        with sub_tab1:
            l_name = st.text_input("닉네임", key="l_name").strip()
            l_pw = st.text_input("비번(4자리)", type="password", key="l_pw", max_chars=4).strip()
            
            if st.button("로그인", use_container_width=True):
                df = load_data(DB_PATH) 
                user_df = df[df['name'].astype(str).str.strip() == l_name] if not df.empty else pd.DataFrame()
                
                if not user_df.empty:
                    # [핵심 수정] 저장된 비번을 문자열로 가져와서 무조건 4자리(0000 형태)로 복원
                    stored_pw = str(user_df.iloc[0]['password']).strip().split('.')[0].zfill(4)
                    input_pw = str(l_pw).strip().zfill(4)
                    
                    if stored_pw == input_pw:
                        st.session_state.logged_in = True
                        st.session_state.user_name = l_name
                        st.session_state.user_pw = input_pw # 0000 형태 유지
                        selected = user_df[user_df['date'].notna()]['date'].unique()
                        st.session_state.selected_dates = set(selected)
                        st.rerun()
                    else:
                        st.error("비밀번호가 틀립니다.")
                else:
                    st.error("등록되지 않은 닉네임입니다.")

        with sub_tab2:
            r_name = st.text_input("등록 닉네임", key="r_name").strip()
            r_pw = st.text_input("등록 비번(4자리)", type="password", key="r_pw", max_chars=4).strip()
            if st.button("등록 완료", use_container_width=True):
                if r_name and len(r_pw) == 4:
                    if not df.empty and r_name in df['name'].astype(str).values:
                        st.warning("이미 존재하는 닉네임입니다.")
                    else:
                        # 비번을 4자리 문자열로 고정해서 저장
                        save_schedule(DB_PATH, r_name, r_pw.zfill(4), [], {})
                        st.success("등록 성공! 로그인 탭으로 이동하세요.")
                else:
                    st.warning("닉네임과 4자리 비번을 정확히 입력하세요.")

    with col_right:
        st.markdown(f"<div class='section-card'><h2>📅 {year}년 {month}월 일정 현황</h2></div>", unsafe_allow_html=True)
        days_header = ["일", "월", "화", "수", "목", "금", "토"]
        h_cols = st.columns(7)
        for i, d in enumerate(days_header):
            h_cols[i].markdown(f"<center><b>{d}</b></center>", unsafe_allow_html=True)

        cal = calendar.monthcalendar(year, month)
        for week in cal:
            w_cols = st.columns(7)
            for i, day in enumerate(week):
                if day == 0: w_cols[i].empty()
                else:
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    count = count_dict.get(date_str, 0)
                    nicknames = names_dict.get(date_str, "참여자 없음")
                    is_best_day = (count > 0 and count == max_count)
                    btn_label = f"{day}\n({count})" if count > 0 else f"{day}"
                    w_cols[i].button(btn_label, key=f"st_{date_str}", help=nicknames, 
                                     use_container_width=True, disabled=True, 
                                     type="primary" if is_best_day else "secondary")

    if st.session_state.logged_in:
        st.divider()
        st.subheader(f"📍 {st.session_state.user_name}님의 일정 수정")
        h_cols_in = st.columns(7)
        for i, d in enumerate(days_header):
            h_cols_in[i].markdown(f"<center><small>{d}</small></center>", unsafe_allow_html=True)

        cal_in = calendar.monthcalendar(year, month)
        for week in cal_in:
            w_cols_in = st.columns(7)
            for i, day in enumerate(week):
                if day == 0: w_cols_in[i].empty()
                else:
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    is_sel = date_str in st.session_state.selected_dates
                    if w_cols_in[i].button(str(day), key=f"sel_{date_str}", use_container_width=True, 
                                          type="primary" if is_sel else "secondary"):
                        if is_sel: st.session_state.selected_dates.remove(date_str)
                        else: st.session_state.selected_dates.add(date_str)
                        st.rerun()
        
        if st.button("💾 내 일정 최종 저장", use_container_width=True):
            # 저장 시에도 4자리 포맷 유지
            save_schedule(DB_PATH, st.session_state.user_name, st.session_state.user_pw.zfill(4), 
                          list(st.session_state.selected_dates), {})
            st.success("저장 완료!")
            st.rerun()

# --- 4. 관리자 탭 ---
with tab_admin:
    st.header("⚙️ 전체 사용자 관리")
    admin_pw = st.text_input("관리자 비밀번호", type="password")
    if admin_pw == "1268":
        st.success("인증 성공")
        # 데이터 다시 불러오기 (비밀번호 컬럼 타입 유지)
        df_admin = load_data(DB_PATH)
        all_users = df_admin['name'].unique() if not df_admin.empty else []
        if len(all_users) > 0:
            target_user = st.selectbox("삭제할 사용자 선택", all_users)
            if st.button(f"❌ {target_user} 삭제 실행"):
                new_df = df_admin[df_admin['name'] != target_user]
                new_df.to_csv(DB_PATH, index=False, encoding='utf-8-sig')
                st.error(f"{target_user} 데이터 삭제됨")
                st.rerun()
            st.divider()
            st.write("📋 현재 전체 데이터 내역")
            # 관리자 화면에서도 비번이 문자열로 보이도록 처리
            st.dataframe(df_admin, use_container_width=True)
        else:
            st.info("등록된 사용자가 없습니다.")
    elif admin_pw != "":
        st.error("비밀번호가 올바르지 않습니다.")
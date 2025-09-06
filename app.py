import streamlit as st
import pandas as pd
import plotly.express as px

# Streamlit 앱 제목 및 기본 설정
st.set_page_config(layout="wide")
st.title("✈️하늘길을 밝히다: 대한민국의 항공 관제 현황")
st.markdown("---")

# 파일 로드 및 데이터 전처리
try:
    df = pd.read_csv("관제탑_관제량_20250906112544.xlsx - 데이터.csv", encoding='utf-8')
except FileNotFoundError:
    st.error("파일을 찾을 수 없습니다. '관제탑_관제량_20250906112544.xlsx - 데이터.csv' 파일이 스크립트와 같은 경로에 있는지 확인해주세요.")
    st.stop()
except UnicodeDecodeError:
    df = pd.read_csv("관제탑_관제량_20250906112544.xlsx - 데이터.csv", encoding='cp949')

# 데이터 정리: '지역(1)' 열을 인덱스로 설정
df = df.rename(columns={'지역(1)': '지역'})
df = df.iloc[1:, :]
df = df.set_index('지역')
df = df.drop(['합계'])

# 날짜 열 이름 변경 (월 정보만 남기기)
df.columns = [col.split('.')[1] + '월' for col in df.columns]

st.header("📈 공항별 월별 관제량 시각화")

# 데이터프레임 구조 변경: wide-to-long
df_long = df.reset_index().melt(id_vars='지역', var_name='월', value_name='관제량')

# 데이터 타입 변환: '관제량'을 숫자로
df_long['관제량'] = pd.to_numeric(df_long['관제량'], errors='coerce')

# --- 사용자 선택 기능 추가 ---
# 사이드바 또는 메인 화면에 선택 박스 생성
st.sidebar.header("🗺️ 공항 선택")
selected_airports = st.sidebar.multiselect(
    '관제량 추이를 확인할 공항을 선택해주세요:',
    options=df['지역'].unique(),
    default=df['지역'].unique()
)

# 선택된 공항 데이터 필터링
filtered_df = df_long[df_long['지역'].isin(selected_airports)]

# Plotly를 사용한 선 그래프 생성
fig = px.line(filtered_df,
              x='월',
              y='관제량',
              color='지역',
              markers=True,
              title='월별 공항 관제량 추이',
              labels={'관제량': '관제량 (대)', '월': '월'})
fig.update_traces(marker_size=10)
fig.update_layout(xaxis_title="기간", yaxis_title="관제량 (대)", legend_title="지역")

# 그래프 시각화
st.plotly_chart(fig, use_container_width=True)

st.write("※ 그래프는 2024년 11월부터 2025년 4월까지의 월별 관제량 데이터를 나타냅니다.")

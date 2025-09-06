import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Streamlit 앱 제목 및 페이지 설정
st.set_page_config(layout="wide")
st.title("✈️하늘길을 밝히다: 대한민국의 항공 관제 현황")
st.markdown("---")

# 📂 파일 경로 설정 및 데이터 로드
file_name = "meals_data.csv"

# 파일 존재 여부 확인
if not os.path.exists(file_name):
    st.error(f"오류: '{file_name}' 파일을 찾을 수 없습니다. 스크립트와 같은 경로에 있는지 확인해주세요.")
    st.stop()

# 파일 인코딩 및 전처리 문제 해결을 위한 try-except 블록
try:
    # 엑셀 파일의 CSV 변환 시 나타나는 메타정보 및 불필요한 열을 제거하고 데이터를 정확히 로드
    # header=1: 두 번째 행을 헤더로 사용
    # usecols='지역(1),2024.11,2024.12,2025.01,2025.02,2025.03,2025.04': 필요한 열만 선택
    # encoding='cp949': 한국어 인코딩 문제 해결
    df = pd.read_csv(file_name, header=1, encoding='cp949')

    # '지역(1)' 열을 '지역'으로 이름 변경
    df = df.rename(columns={'지역(1)': '지역'})
    
    # '지역' 열에 값이 있는 행만 선택하여 빈 값을 가진 행과 합계 행 제거
    df = df[df['지역'].notna() & (df['지역'] != '합계')]

    # 열 이름에서 '연도.월' 형식을 '월'로 변경 (예: '2024.11' -> '11월')
    new_columns = ['지역'] + [col.split('.')[1] + '월' for col in df.columns[1:]]
    df.columns = new_columns
    
    # 데이터프레임 구조 변경 (시각화를 위해)
    df_long = df.melt(id_vars='지역', var_name='월', value_name='관제량')
    df_long['관제량'] = pd.to_numeric(df_long['관제량'], errors='coerce')
    
    # '지역'을 인덱스로 설정
    df = df.set_index('지역')
    
except Exception as e:
    st.error(f"데이터 전처리 중 오류가 발생했습니다. 원본 파일의 형식이 올바른지 확인해주세요. 오류: {e}")
    st.stop()


## 📊 사용자 선택 및 시각화

st.header("📈 공항별 월별 관제량 시각화")

# 사이드바에 공항 선택 멀티박스 추가
st.sidebar.header("🗺️ 공항 선택")
selected_airports = st.sidebar.multiselect(
    '관제량 추이를 확인할 공항을 선택해주세요:',
    options=df.index.unique().tolist(),
    default=df.index.unique().tolist()
)

# 선택된 공항 데이터 필터링
filtered_df = df_long[df_long['지역'].isin(selected_airports)]

if filtered_df.empty:
    st.warning("선택된 공항의 데이터가 없습니다. 다른 공항을 선택해주세요.")
else:
    # Plotly를 사용한 선 그래프 생성
    fig = px.line(filtered_df,
                  x='월',
                  y='관제량',
                  color='지역',
                  markers=True,
                  title='선택 공항의 월별 관제량 추이',
                  labels={'관제량': '관제량 (대)', '월': '월'})
    fig.update_traces(marker_size=10)
    fig.update_layout(xaxis_title="기간", yaxis_title="관제량 (대)", legend_title="지역")
    
    # 그래프 시각화
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("※ 그래프는 2024년 11월부터 2025년 4월까지의 월별 관제량 데이터를 나타냅니다.")


## 📋 원본 데이터

st.subheader("📋 원본 데이터")
st.dataframe(df)

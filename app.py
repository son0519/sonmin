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

# 파일 인코딩 문제 해결을 위한 try-except 블록
try:
    df = pd.read_csv(file_name, encoding='utf-8')
except UnicodeDecodeError:
    try:
        df = pd.read_csv(file_name, encoding='cp949')
    except UnicodeDecodeError:
        st.error("오류: 파일 인코딩을 감지할 수 없습니다. 파일을 메모장으로 열어 UTF-8 형식으로 다시 저장해주세요.")
        st.stop()
except Exception as e:
    st.error(f"파일을 읽는 도중 예상치 못한 오류가 발생했습니다: {e}")
    st.stop()

# 🧹 데이터 전처리
try:
    # 첫 번째 열을 '지역'으로 가정하고 이름 변경
    df = df.rename(columns={df.columns[0]: '지역'})
    
    # '합계' 행 제거 (대소문자 및 공백을 고려)
    if '합계' in df['지역'].values:
        df = df[df['지역'] != '합계']
    
    # 불필요한 첫 행 제거 (만약 필요하다면)
    df = df.iloc[1:, :]
    
    # '지역' 열을 인덱스로 설정
    df = df.set_index('지역')

    # 열 이름에서 연도 정보 제거 후 '월' 추가 (예: '2024.11' -> '11월')
    new_columns = []
    for col in df.columns:
        if '.' in col:
            new_columns.append(col.split('.')[1] + '월')
        else:
            new_columns.append(col)
    df.columns = new_columns

    # 데이터프레임 구조 변경 (시각화를 위해)
    df_long = df.reset_index().melt(id_vars='지역', var_name='월', value_name='관제량')
    df_long['관제량'] = pd.to_numeric(df_long['관제량'], errors='coerce')

except Exception as e:
    st.error(f"데이터 전처리 중 오류가 발생했습니다. 원본 파일의 형식이 올바른지 확인해주세요. 오류: {e}")
    st.stop()

# ---
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

---

## 📋 원본 데이터

st.subheader("📋 원본 데이터")
st.dataframe(df)

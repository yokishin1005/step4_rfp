import streamlit as st
import pandas as pd
import altair as alt
from sqlalchemy import create_engine, func, extract, or_
from sqlalchemy.orm import sessionmaker
from datetime import datetime, time
from models import UserMaster, ReservationRecords, Base

# データベース接続
engine = create_engine('sqlite:///rfp.db')
Session = sessionmaker(bind=engine)

TIME_RANGES = {
    '早朝（8:00-10:00）': ('08:00', '10:00'),
    '朝(10:00-12:00)': ('10:00', '12:00'),
    '正午(12:00-13:00)': ('12:00', '13:00'),
    '午後(13:00-16:00)': ('13:00', '16:00'),
    '夕方(16:00-18:00)': ('16:00', '18:00'),
    '夜(18:00-20:00)': ('18:00', '20:00')
}

def calculate_age(birthdate):
    today = datetime.now()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

def create_chart(data, title):
    # データフレームに変換し、カラム名を明示的に指定
    df = pd.DataFrame({'category': data.index, 'count': data.values})
    
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('category:N', axis=alt.Axis(labelAngle=-45), title=None),
        y=alt.Y('count:Q', title='人数'),
        color=alt.Color('category:N', legend=None),
        tooltip=['category', 'count']
    ).properties(
        title=title,
        width=alt.Step(40)
    )
    text = chart.mark_text(
        align='center',
        baseline='bottom',
        dy=-5
    ).encode(
        text='count:Q'
    )
    return (chart + text).interactive()

def main():
    st.set_page_config(page_title="来意患者傾向分析", layout="wide")
    st.title('来意患者傾向分析ダッシュボード')

    session = Session()

    # サイドバーにフィルター条件を配置
    st.sidebar.header('フィルター条件')

    # 年月フィルター
    min_date = session.query(func.min(ReservationRecords.reservation_date)).scalar()
    max_date = session.query(func.max(ReservationRecords.reservation_date)).scalar()
    years = range(min_date.year, max_date.year + 1)
    months = range(1, 13)

    current_year = datetime.now().year
    current_month = datetime.now().month

    selected_year = st.sidebar.selectbox('年を選択', years, index=list(years).index(current_year) if current_year in years else 0)
    selected_month = st.sidebar.selectbox('月を選択', months, index=current_month - 1)

    # 時間帯フィルター
    selected_time_zones = st.sidebar.multiselect(
        '時間帯を選択',
        list(TIME_RANGES.keys()),
        default=list(TIME_RANGES.keys())
    )

    # クエリの構築
    query = session.query(UserMaster).join(ReservationRecords).filter(
        extract('year', ReservationRecords.reservation_date) == selected_year,
        extract('month', ReservationRecords.reservation_date) == selected_month
    )
    
    if selected_time_zones:
        time_conditions = [
            func.time(ReservationRecords.start_time).between(TIME_RANGES[zone][0], TIME_RANGES[zone][1])
            for zone in selected_time_zones
        ]
        query = query.filter(or_(*time_conditions))

    users = query.all()

    # 分析結果の表示
    if users:
        st.header(f'{selected_year}年{selected_month}月の分析結果')

        # 全体のサマリー
        total_users = len(users)
        st.subheader(f'総患者数: {total_users}人')

        # メトリクス
        col1, col2, col3 = st.columns(3)
        profession_counts = pd.Series([user.profession for user in users]).value_counts()
        gender_counts = pd.Series([user.gender for user in users]).value_counts()
        ages = [calculate_age(user.birthday) for user in users]
        
        with col1:
            st.metric("最も多い職業", profession_counts.index[0], f"{profession_counts.values[0]}人 ({profession_counts.values[0]/total_users:.1%})")
        with col2:
            st.metric("性別比率", f"{gender_counts.index[0]}/{gender_counts.index[1]}", f"{gender_counts.values[0]}/{gender_counts.values[1]}")
        with col3:
            st.metric("平均年齢", f"{sum(ages)/len(ages):.1f}歳", f"最年少{min(ages)}歳 - 最年長{max(ages)}歳")

        st.markdown("---")

        # 詳細な分布
        st.subheader("詳細な分布")
        
        tab1, tab2, tab3 = st.tabs(["職業分布", "性別分布", "年齢分布"])
        
        with tab1:
            st.altair_chart(create_chart(profession_counts, "職業分布"), use_container_width=True)
        
        with tab2:
            st.altair_chart(create_chart(gender_counts, "性別分布"), use_container_width=True)
        
        with tab3:
            age_ranges = [f"{i}-{i+4}" for i in range(0, max(ages)+5, 5)]
            age_counts = pd.cut(ages, bins=range(0, max(ages)+5, 5), right=False, labels=age_ranges[:-1]).value_counts().sort_index()
            st.altair_chart(create_chart(age_counts, "年齢分布"), use_container_width=True)

    else:
        st.warning('選択された条件のデータがありません。')

    session.close()

if __name__ == '__main__':
    main()
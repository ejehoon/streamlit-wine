import streamlit as st
import pandas as pd

# 구글 스프레드시트에서 데이터 로드
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1XZ_jqpTmFbGzDQ47XHyEq01BFXfhldgSoWLMhMiCR4g/export?format=csv"
base_total = pd.read_csv(spreadsheet_url)

# 스트림릿 앱 구현
st.title("와인 추천 시스템")

menu = st.sidebar.selectbox("메뉴 선택", ["와인 추천", "와인 검색", "리뷰 작성", "와인정보검색"])

if menu == "와인정보검색":
    st.header("와인정보검색")
    st.markdown("아래에서 `모두와인` 사이트를 직접 확인하세요:")
    st.components.v1.iframe("https://modu.wine/wine_search", height=800, scrolling=True)

elif menu == "와인 추천":
    st.header("와인 추천")
    type_map = {1: "레드 와인", 2: "화이트 와인", 3: "로제 와인", 4: "샴페인"}
    type_input = st.selectbox("와인 종류를 선택하세요", options=list(type_map.keys()), format_func=lambda x: type_map[x])
    selected_type = type_map[type_input]
    price = st.number_input("선호 가격 (원)", min_value=0, step=1000)
    alcohol = st.slider("알코올 함량 (%)", 0.0, 20.0, step=0.1)
    tannin = st.slider("탄닌감 (1~5)", 1, 5, step=1)
    acidity = st.slider("산미 (1~5)", 1, 5, step=1)

    if st.button("추천 받기"):
        recommendations = []
        for _, row in base_total.iterrows():
            score = 0
            if row["Type"] == selected_type:
                score += 1
            if price * 0.9 <= row["Price"] <= price * 1.1:
                score += 1
            if alcohol * 0.9 <= row["Alcohol"] <= alcohol * 1.1:
                score += 1
            if tannin - 1 <= row["Tannin"] <= tannin + 1:
                score += 1
            if acidity - 1 <= row["Acidity"] <= acidity + 1:
                score += 1

            recommendations.append({
                "Name": row["Name"],
                "Type": row["Type"],
                "Price": row["Price"],
                "Alcohol": row["Alcohol"],
                "Tannin": row["Tannin"],
                "Acidity": row["Acidity"],
                "Flavor_note": row["Flavor_note"],
                "Review": row["Review"],
                "Score": score
            })

        recommendations = sorted(recommendations, key=lambda x: x["Score"], reverse=True)[:5]

        if recommendations:
            st.subheader("추천 와인 목록")
            for wine in recommendations:
                st.write(f"""
                **이름:** {wine['Name']}
                **종류:** {wine['Type']}
                **가격:** {wine['Price']}원
                **알코올:** {wine['Alcohol']}%
                **탄닌:** {wine['Tannin']}/5
                **산미:** {wine['Acidity']}/5
                **풍미:** {wine['Flavor_note']}
                **리뷰:** {wine['Review']}
                """)
        else:
            st.warning("조건에 맞는 와인을 찾을 수 없습니다.")

elif menu == "와인 검색":
    st.header("와인 검색")
    name = st.text_input("검색하실 와인 이름을 입력해주세요 (일부 입력 가능): ").strip().lower()

    if st.button("검색"):
        searched = base_total[base_total["Name"].str.contains(name, na=False, case=False)].head(5)

        if not searched.empty:
            st.subheader("검색 결과")
            for _, wine in searched.iterrows():
                st.write(f"""
                **이름:** {wine['Name']}
                **종류:** {wine['Type']}
                **가격:** {wine['Price']}원
                **알코올:** {wine['Alcohol']}%
                **탄닌:** {wine['Tannin']}/5
                **산미:** {wine['Acidity']}/5
                **풍미:** {wine['Flavor_note']}
                **리뷰:** {wine['Review']}
                """)
        else:
            st.warning("검색하신 와인을 찾을 수 없습니다.")

elif menu == "리뷰 작성":
    st.header("리뷰 작성")
    wine_name = st.text_input("리뷰를 작성할 와인의 이름을 입력해주세요 (일부 입력 가능): ").strip().lower()

    if st.button("리뷰 추가"):
        matched_wines = base_total[base_total["Name"].str.contains(wine_name, na=False, case=False)]

        if not matched_wines.empty:
            st.subheader("검색 결과")
            wine_options = {idx: f"{wine['Name']} | 종류: {wine['Type']} | 가격: {wine['Price']}원" for idx, wine in matched_wines.iterrows()}
            selected_idx = st.selectbox("리뷰를 작성할 와인을 선택해주세요:", options=list(wine_options.keys()), format_func=lambda x: wine_options[x])

            review_text = st.text_area("작성할 리뷰를 입력해주세요: ").strip()
            if st.button("리뷰 저장"):
                base_total.at[selected_idx, "Review"] = review_text
                st.success(f"{matched_wines.at[selected_idx, 'Name']}에 대한 리뷰가 성공적으로 저장되었습니다.")
        else:
            st.warning("해당 이름의 와인을 찾을 수 없습니다.")

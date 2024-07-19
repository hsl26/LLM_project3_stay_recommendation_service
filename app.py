import streamlit as st
import response_by_llm as r
import json
import retrieval as ree
import re
st.title('숙박 추천 서비스')

def select():

    with st.form('my_form'):
        region = st.text_input('숙박 예정 지역을 입력해 주세요 (예: 제주도 서귀포시 ... )')

        accommodation = st.multiselect(
            '숙박 형태',
            ['호텔', '모텔', '펜션', '리조트', '게스트하우스', '한옥', '홈스테이', '민박']
        )

        facility = st.multiselect(
            '시설',
            ['-', '피트니스', '수영장', '스파', '사우나', '세미나룸', '노래방', '미용시설', '바베큐'] 
        )

        submitted = st.form_submit_button('완료')

    if submitted:
       if not region:
           st.error('숙박 예정 지역을 입력해 주세요.')
       elif not accommodation:
            st.error("숙박 형태를 최소 1개 선택해 주세요.")
       elif not facility:
            st.error('시설을 최소 1개 선택해 주세요.')
       else:
            dic = {
                'region': region,
                'accommodation': accommodation,
                'facility': facility,
            }

            return dic

def display_recommendations(recommendations_list):
    if "no stay" in recommendations_list:
        st.markdown("검색 결과가 없습니다. 다시 검색해보세요.")
    else:
        st.markdown("## 추천 결과")
        for idx, rec in enumerate(recommendations_list, start=1):
            st.markdown(f"""
            <div style="border: 1px solid #ddd; border-radius: 10px; padding: 10px; margin-bottom: 10px;">
                <h3 style="color: #2C3E50;">{idx}. {rec['name']}</h3>
                <p><strong>특징:</strong> {rec['features']}</p>
                <p><strong>부대시설:</strong> {rec['facility']}</p>
                <p><strong>위치:</strong> {rec['location']}</p>
                <p><strong>추천 이유:</strong> {rec['recommendation']}</p>
                <p><strong>전화번호:</strong> {rec['phone']}</p>
                <p><strong>체크인:</strong> {rec['checkin']}</p>
                <p><strong>체크아웃:</strong> {rec['checkout']}</p>
            </div>
            """, unsafe_allow_html=True)
        

if __name__ == '__main__':
    dic = select()
    if dic is not None:
        region = dic["region"]
        accommodation = ','.join(dic["accommodation"])
        facility = ','.join(dic["facility"])
        input_text = f"지역 정보 : {region}, 숙박 형태 : {accommodation}"
        output_text = ree.good(input_text)
        print(output_text)

        
        if "no stay" in output_text:
            display_recommendations(output_text)
        else: 
            json_match = re.search(r'\[.*\]', output_text, re.DOTALL)
            
            json_string = json_match.group()
            
            output_text = json.loads(json_string)
            print(type(output_text))
            print(output_text)
            display_recommendations(output_text)
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from langchain_teddynote.prompts import load_prompt


key = st.secrets['OPENAI_API_KEY']

# 페이지 설정
st.set_page_config(page_title="번역기", page_icon="🌍", layout="wide")

st.title('번역 챗봇')

st.markdown("""
<style>
@media (max-width: 600px) {
  .stApp {
    max-width: 100%;
  }
}
</style>
""", unsafe_allow_html=True)

class ConverSationSummary_KOR(BaseModel):
    original_korean_sentence: str = Field(description="원문 한국어 문장")
    translated_vietnamese_sentence: str = Field(description="번역된 베트남어 문장")
    context_precautions_of_translation: str = Field(description="번역의 맥락이나 주의사항")

parser_kor = PydanticOutputParser(pydantic_object=ConverSationSummary_KOR)     

class ConverSationSummary_VT(BaseModel):
    original_vietnamese_sentence: str = Field(description="원문 베트남어 문장")
    translated_korean_sentence: str = Field(description="번역된 한국어 문장")
    context_precautions_of_translation: str = Field(description="번역의 맥락이나 주의사항")

parser_vt = PydanticOutputParser(pydantic_object=ConverSationSummary_VT)  


# CSS 스타일 적용
st.markdown("""
<style>
body {
    background: linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%);
    color: #1e3799;
}
.stApp {
    background: rgba(255, 255, 255, 0.7);
    border-radius: 20px;
    padding: 20px;
}
h1 {
    color: #4a69bd;
    text-align: center;
    font-size: 3em;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}
.lang-button {
    background-color: #54a0ff;
    color: white;
    padding: 10px 20px;
    border-radius: 10px;
    border: none;
    font-size: 18px;
    margin: 10px;
    transition: all 0.3s;
}
.lang-button:hover {
    background-color: #5f27cd;
    transform: translateY(-3px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)

# 앱 제목
st.markdown("<h3 style='text-align: center;'>김궁영 형님 언어 번역기</h3>", unsafe_allow_html=True)


def ask(user_input, prompt_pype):

    if prompt_pype == 'ko':
        prompt = load_prompt('./prompts/prompt_kor.yaml')
        prompt = prompt.partial(format=parser_kor.get_format_instructions())
        
        llm = ChatOpenAI(
            api_key=key,
            model='gpt-4o',	    
            temperature=0,		        
        )
        
        chain = prompt | llm    

        response = chain.invoke({'question': user_input})
        structured_output = parser_kor.parse(response.content)  

        return structured_output

    else:
        prompt = load_prompt('./prompts/prompt_v.yaml')
        prompt = prompt.partial(format=parser_vt.get_format_instructions())

        llm = ChatOpenAI(
            api_key=key,
            model='gpt-4o',	    
            temperature=0,		        
        )

        chain = prompt | llm    

        response = chain.invoke({'question': user_input})
        structured_output = parser_vt.parse(response.content)  # 객체로 만들기 

        return structured_output
    


# 언어 선택 버튼
col1, col2 = st.columns(2)
with col1:
    if st.button("🇰🇷 한국어 → 🇻🇳 베트남어", key="ko_to_vi", help="한국어를 베트남어로 번역합니다", use_container_width=True):
        st.session_state.translation_direction = "ko_to_vi"
with col2:
    if st.button("🇻🇳 베트남어 → 🇰🇷 한국어", key="vi_to_ko", help="베트남어를 한국어로 번역합니다", use_container_width=True):
        st.session_state.translation_direction = "vi_to_ko"

# 번역 방향에 따른 입력 필드 표시
if 'translation_direction' in st.session_state:
    if st.session_state.translation_direction == "ko_to_vi":
        prompt_type = 'ko'
    else:
        prompt_type = 'vi'

    # chain = create_chain(prompt_type)

    if st.session_state.translation_direction == "ko_to_vi":
        user_input = st.text_area("한국어 텍스트를 입력하세요:", height=150)

        if st.button("번역하기 🚀", key="translate_ko_to_vi"):

            with st.spinner('AI 번역 중..'):
                structured_output = ask(user_input, prompt_type)

                expander_translation_kor = st.empty()
                
                with expander_translation_kor.expander('AI 번역 결과', expanded=True):
                    original_sentence = structured_output.original_korean_sentence
                    translated_sentence = structured_output.translated_vietnamese_sentence
                    context_precautions_of_translation = structured_output.context_precautions_of_translation


                    # 색깔이 있는 텍스트 출력
                    st.markdown(f"<p style='color: blue; font-size: 16px;'>원문 한국어 문장: {original_sentence}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color: green; font-size: 16px;'>번역된 베트남어 문장: {translated_sentence}</p>", unsafe_allow_html=True)
                    st.markdown("<hr>", unsafe_allow_html=True)  # 구분선 추가

                    container = st.empty()  # 빈 공간에 스트리밍 출력
                    answer = ''             # 최종 결과 저장 변수

                    for token in context_precautions_of_translation:        # 실시간으로 스트리밍 출력
                        answer += token
                        container.markdown(f"<p style='color: orange; font-size: 14px;'>{answer}</p>", unsafe_allow_html=True)

                    st.success("🎉 번역 완료! 🇻🇳")
                    st.code(translated_sentence, language="text")  # 번역 결과만 표시

    else:
        user_input = st.text_area("베트남어 텍스트를 입력하세요:", height=150)

        if st.button("번역하기 🚀", key="translate_vi_to_ko"):
            structured_output = ask(user_input, prompt_type)

            with st.spinner('AI 번역 중..'):
                structured_output = ask(user_input, prompt_type)

                expander_translation_kor = st.empty()
                
                with expander_translation_kor.expander('AI 번역 결과', expanded=True):
                    original_sentence = structured_output.original_vietnamese_sentence
                    translated_sentence = structured_output.translated_korean_sentence
                    context_precautions_of_translation = structured_output.context_precautions_of_translation


                    # 색깔이 있는 텍스트 출력
                    st.markdown(f"<p style='color: blue; font-size: 16px;'>원문 베트남어 문장: {original_sentence}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color: green; font-size: 16px;'>번역된 한국어 문장: {translated_sentence}</p>", unsafe_allow_html=True)
                    st.markdown("<hr>", unsafe_allow_html=True)  # 구분선 추가


                    container = st.empty()  # 빈 공간에 토큰을 스트리밍 출력
                    answer = ''  # 최종 번역 결과를 저장할 변수

                    for token in context_precautions_of_translation:
                        answer += token
                        container.markdown(f"<p style='color: orange; font-size: 14px;'>{answer}</p>", unsafe_allow_html=True)  

                    translation_result = answer.strip()  # 최종 번역 결과 저장
                    st.success("🎉 번역 완료! 🇻🇳")
                    st.code(translated_sentence, language="text")  # 번역 결과만 표시
            
# 푸터
st.markdown("---")
st.markdown("Made with ❤️ by 이인환")
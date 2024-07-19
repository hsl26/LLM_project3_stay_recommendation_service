from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from dotenv import load_dotenv
import os

import db

def good(input_text) :

    load_dotenv()

    # def get_retrieval():
    # db에서 데이터 받아서 문자열로 변경 (주소, 이름, type) 
    db_data = db.fetch_rows()

    def tuples_to_strings(db_data):
        return [' '.join(map(str, tpl[1:])) for tpl in db_data]

    stay_info_list = tuples_to_strings(db_data)

    stay_info_txt = '/n '.join(stay_info_list)

    stay_info_document = Document(
        page_content=stay_info_txt,
        metadata={"source": "숙박 정보"}
    )



    recursive_text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n"], 
        chunk_size=40,
        chunk_overlap=10,
        length_function=len,
    )


    recursive_splitted_document = recursive_text_splitter.split_documents([stay_info_document])


    embedding_model=AzureOpenAIEmbeddings(
        model="text-embedding-3-large"
    )


    chroma = Chroma("vector_store")
    vector_store = chroma.from_documents(
            documents=recursive_splitted_document,
            embedding=embedding_model
        )


    similarity_retriever = vector_store.as_retriever(search_type="similarity")
    mmr_retriever = vector_store.as_retriever(search_type="mmr")
    similarity_score_retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold", 
            search_kwargs={"score_threshold": 0.2}
        )

    retriever = similarity_retriever
        
        # return retriever


    # ---------------------------------------------------------------------

    # Generate

    # retriever = get_retrieval()

    system_prompt_str = """
            You are an assistant for question-answering tasks. 
            Use the following pieces of retrieved context to answer the question. 
            If you don't know the answer, just say that you don't know. 
            Use three sentences maximum and keep the answer concise.
            Answer for the question in Korean.
            추천할 때는 최대 3개 추천해줘. 
            만약에 단 1도 찾을 수 없다면. "no stay"을 출력해줘. 예시를 줄건데 예시를 그대로 출력하지마.
            특징, 위치, 추천 이유, 전화번호는 무조건 포함시켜. 예시처럼 json.loads하면 바로 파이썬 dict로 바꿀수 있는 문자열 출력해줘. ex) [
                {{
                    "name": "쉐라톤 서울 디큐브 시티 호텔",
                    "features": "현대적인 객실, 고급 레스토랑, 피트니스 센터, 실내 수영장을 갖추고 있습니다.",
                    "facility": "수영장",
                    "location": "서울특별시 구로구 경인로 662",
                    "recommendation": "편리한 교통, 고급스러운 시설, 다양한 고급스러운 부대시설 제공",
                    "phone": "02-2211-2000",
                    "checkin": "15:00",
                    "checkout": "11:00"
                }},
                // 예시니까 위의 예시를 그대로 출력하지 말것. format일 뿐이다.
            ]
            
            {context}
            """.strip()

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt_str),
            ("human", "{input}"),
        ]
    )

    azure_model = AzureChatOpenAI(
        azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    )

    question_answer_chain = create_stuff_documents_chain(azure_model, prompt_template)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    chain_output = rag_chain.invoke({"input":input_text})
        # print("\n",chain_output,"\n")
    return chain_output["answer"]
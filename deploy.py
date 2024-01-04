import os.path
import os
import PyPDF2
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space 
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
from llama_index import (
    Document,
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
path = "المقاولة والأعمال\الصفقات العمومية"

# Side bar contents
with st.sidebar:
    st.title('الذكاء الاصطناعي أشبال')
    st.markdown('''
    ## معلومات عنا:
    - [Achbal Mail](mailto:achbal.business@gmail.com)
    
    هذا التطبيق هو تواصل مع الذكاء الاصطناعي أشبال مدعومة ب (LLM) تم بناؤه باستخدام:
    - [Streamlit](https://streamlit.io/)
    - [OpenAI](https://platform.openai.com/docs/models) LLM Model
    - [Idarati dataset](https://www.idarati.ma/)
    ''')
    add_vertical_space(5)
    st.write('تم إنشاؤه من قبل فريق أشبال')
st.title('تواصل مع الذكاء الاصطناعي أشبال')



if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant",  "content": "اسألني سؤالاً حول مكتبة مستندات مفتوحة المصدر Idarati !"}
    ]
#Start from page 6 to page 955
#Start from page 6 to page 955
pdf_path = "HWFWM1.pdf"
start_page = 6
end_page = 955
HWFWM_text = ""
with open(pdf_path, "rb") as file:
    reader = PyPDF2.PdfReader(file)
    num_pages = len(reader.pages)

    if start_page > num_pages or end_page > num_pages:
        print("Invalid page range.")
    else:
        text = ""
        for page_num in range(start_page + 1, end_page):
            page = reader.pages[page_num]
            text += page.extract_text()

        HWFWM_text = text
        print(HWFWM_text)

@st.cache_resource(show_spinner=False)
def load_index():
    with st.spinner(text="جاري تحميل  مستندات اداراتي  انتظر قليلاً! قد يستغرق هذا الأمر من 1 إلى 2 دقيقة."):
        if not os.path.exists("./storage"):
            # load the documents and create the index
            # documents = SimpleDirectoryReader(path).load_data()
            document = Document(
                id_='c44713bb-32e4-4aaa-976b-4d9b4cd9273e',
                embedding=None,
                excluded_embed_metadata_keys=[
                    'file_name', 'file_type', 'file_size', 'creation_date',
                    'last_modified_date', 'last_accessed_date'
                ],
                excluded_llm_metadata_keys=[
                    'file_name', 'file_type', 'file_size', 'creation_date',
                    'last_modified_date', 'last_accessed_date'
                ],
                relationships={},
                hash='eca215ab1876fab827b2f5fc08b2ca1a254cb40b12374a53069977e8624b5963',
                text=HWFWM_text,
                start_char_idx=None,
                end_char_idx=None,
                text_template='{metadata_str}\n\n{content}',
                metadata_template='{key}: {value}',
                metadata_seperator='\n'
            )
            index = load_index()

            # Get indexes from HWFWM_text using VectorStoreIndex
            vector_index = VectorStoreIndex.from_document(document)
            indexes = vector_index.indexes

            for idx in indexes:
                print(idx)
            # index = VectorStoreIndex.from_document(document)
            # store it for later
            index.storage_context.persist()
        else:
            # load the existing index
            storage_context = StorageContext.from_defaults(persist_dir="./storage")
            index = load_index_from_storage(storage_context)
        return index
index = load_index()


if "chat_engine" not in st.session_state.keys(): # Initialize the chat engine
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)
# either way we can now query the index
# query_engine = index.as_query_engine()

if prompt := st.chat_input(" أدخل سؤالك هنا"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("جارٍ التفكير..."):
            try:
                response = st.session_state.chat_engine.chat(prompt)
                st.write(response.response)
                message = {"role": "assistant", "content": response.response}
                st.session_state.messages.append(message) # Add response to message history
            except  Exception as e:
                st.error("!تم استنفاد طلبات مفتاح المجانية. يرجى النظر في الانتظار لمدة دقيقة")
                st.error("!في هذه الأثناء، فكر في الاتصال بالمطورين لأي سؤال أو رغبة في رعاية هذا المشروع")
            # response = st.session_state.chat_engine.chat(prompt)
            # st.write(response.response)
            # message = {"role": "assistant", "content": response.response}
            # st.session_state.messages.append(message) # Add response to message history        
# query = st.text_input("What would you like to know about your PDF?")
    
# if query:
#     print(type(query))
#     response = query_engine.query(query)
#     st.write(response)
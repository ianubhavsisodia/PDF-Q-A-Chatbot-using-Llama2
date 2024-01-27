import nest_asyncio
import streamlit as st
import json
import os
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from llama_index import ServiceContext, set_global_service_context
from llama_index import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings import GradientEmbedding
from llama_index.llms import GradientBaseModelLLM
from copy import deepcopy
from tempfile import NamedTemporaryFile

    

nest_asyncio.apply()

@st.cache_resource
def create_datastax_connection():
    cloud_config = {'secure_connect_bundle': 'secure-connect-Anubhav.zip'}

    with open("anubhavsisodia-token.json") as f:
        secrets = json.load(f)

    CLIENT_ID = secrets["clientId"]
    CLIENT_SECRET = secrets["secret"]

    auth_provider = PlainTextAuthProvider(CLIENT_ID, CLIENT_SECRET)
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    astra_session = cluster.connect()
    return astra_session

def initialize_session_state():
    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    if "activate_chat" not in st.session_state:
        st.session_state.activate_chat = False

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "query_engine" not in st.session_state:
        st.session_state.query_engine = None

def create_temp_directory():
    # Get the current working directory (where the script is located)
    current_directory = os.getcwd()

    # Create a temporary directory in the same folder
    temp_dir = os.path.join(current_directory, 'temp_directory')
    os.makedirs(temp_dir, exist_ok=True)

    return temp_dir

def main():
    index_placeholder = None
    st.set_page_config(page_title="Chat with your PDF using Llama2 & Llama Index", page_icon="🦙")
    st.header('🤖Chat with your PDF using Llama2 model & Llama Index')

    initialize_session_state()

    session = create_datastax_connection()

    os.environ['GRADIENT_ACCESS_TOKEN'] = "empPxvWteo5J5lEjb4nCM3bjpUSu0Mlp"
    os.environ['GRADIENT_WORKSPACE_ID'] = "13fb9b3a-fb5f-45e6-a42d-3a0558554b56_workspace"

    llm = GradientBaseModelLLM(base_model_slug="llama2-7b-chat", max_tokens=400)

    embed_model = GradientEmbedding(
        gradient_access_token=os.environ["GRADIENT_ACCESS_TOKEN"],
        gradient_workspace_id=os.environ["GRADIENT_WORKSPACE_ID"],
        gradient_model_slug="bge-large")

    service_context = ServiceContext.from_defaults(
        llm=llm,
        embed_model=embed_model,
        chunk_size=256)

    set_global_service_context(service_context)

    with st.sidebar:
        st.subheader('Upload Your PDF File')
        docs = st.file_uploader('⬆️ Upload your PDF & Click to process',
                                accept_multiple_files=False,
                                type=['pdf'])
        # Check if a file is uploaded
        if docs:
            # Store the uploaded file in session state
            st.session_state.uploaded_file = docs
            st.success("File uploaded successfully!")
            # Display processing button only when a file is uploaded
            if st.button('Process'):
                with st.spinner('Processing'):
                        # Specify a specific directory for the temporary file
                        temp_dir = create_temp_directory()
                        with NamedTemporaryFile(dir=temp_dir, suffix='.pdf', delete=False) as f:
                            temp_filename = f.name
                            f.write(st.session_state.uploaded_file.getbuffer())
                            documents = SimpleDirectoryReader(temp_dir).load_data()
                            index = VectorStoreIndex.from_documents(documents, service_context=service_context)
                            query_engine = index.as_query_engine()
                            st.session_state.query_engine = query_engine
                            st.session_state.activate_chat = True
    if st.session_state.activate_chat:
        prompt = st.chat_input("Ask your question from the PDF?")
        if prompt:
            with st.chat_message("user", avatar='👨🏻'):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "avatar": '👨🏻', "content": prompt})

            pdf_response = st.session_state.query_engine.query(prompt)
            cleaned_response = pdf_response.response
            with st.chat_message("assistant", avatar='🤖'):
                st.markdown(cleaned_response)
            st.session_state.messages.append({"role": "assistant", "avatar": '🤖', "content": cleaned_response})
        else:
            st.markdown('Upload your PDFs to chat')

if __name__ == '__main__':
    main()

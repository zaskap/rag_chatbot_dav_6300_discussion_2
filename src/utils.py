'''
utils.py consists of all template, input and other utility functions of loki
'''

import streamlit as st # Import Streamlit library
from streamlit_chat import message # Import message function from streamlit_chat library to render chat
from configparser import ConfigParser # Import ConfigParser library to read config file for greeting
from chat import initialize_chat # Import initialize_chat function from chat.py to initialise chat upon clearing session state
from PIL import Image # Import Image from PIL library to save image uploaded by user
import json


bucket='<S3_Bucket_Name>'
prefix='gen-ai-qa'
region_name='<AWS_Region>'


application_metadata = {
     'models-llm':[
        {'name': 'Nova-Pro','endpoint':"us.amazon.nova-pro-v1:0"},
        {'name': 'claude3.5-sonnetV2','endpoint':"us.anthropic.claude-3-5-sonnet-20241022-v2:0"},
        {'name':'claude3-sonnet', 'endpoint':"anthropic.claude-3-sonnet-20240229-v1:0"},
        {'name': 'claude3.5-sonnet','endpoint':"anthropic.claude-3-5-sonnet-20240620-v1:0"},
        {'name': 'deepseek-R1','endpoint':"us.deepseek.r1-v1:0"},
        {'name':'AI21-J2-mid', 'endpoint':'ai21.j2-mid'},
        {'name':'AI21-J2-ultra', 'endpoint':'ai21.j2-ultra-v1'},
        {'name':'Cohere Command', 'endpoint':"cohere.command-text-v14"},
        {'name':'Titan', 'endpoint':"amazon.titan-text-express-v1"},
        {'name':'Llama3-8b-instruct', 'endpoint':"meta.llama3-8b-instruct-v1:0"},
        {'name':'Llama-31-70b-instruct', 'endpoint':"meta.llama3-1-70b-instruct-v1:0"},
        {'name':'mistral-7b', 'endpoint':"mistral.mistral-7b-instruct-v0:2"},
        {'name':'mixtral-8x7b-instruct', 'endpoint':"mistral.mixtral-8x7b-instruct-v0:1"}
       ],
    'models-emb':[
        {'name':'Titan', 'endpoint':'amazon.titan-embed-text-v1'},
        ],
    'summary_model':'cohere-gpt-medium',
    'region':region_name,
    'kendra_index':'<update-Your-Kendra-IndexID>',
    'datastore':
        {'bucket':bucket, 'prefix':prefix},
    'opensearch':
        {'es_username':'username', 'es_password':'password', 'domain_endpoint':'<OpenSeach Domain Endpoint>'},    
}

json.dump(application_metadata, open('application_metadata_complete.json', 'w'))

APP_MD    = json.load(open('application_metadata_complete.json', 'r'))
MODELS_LLM = {d['name']: d['endpoint'] for d in APP_MD['models-llm']}
MODELS_EMB = {d['name']: d['endpoint'] for d in APP_MD['models-emb']}
MODEL_SUM = APP_MD['summary_model']
REGION    = APP_MD['region']
BUCKET    = APP_MD['datastore']['bucket']
PREFIX    = APP_MD['datastore']['prefix']


#
config_object = ConfigParser() # Read config file for greeting
config_object.read("./config.ini") #
greeting=config_object["MSG"]["greeting"] #
#


# function to display document input options and return the input choice and uploaded file
# this function is called from the main.py file
def input_selector():
        # Removed YouTube as the Input choice due to YY blocking static IP and hence YouTube API throws error when tried from Cloud based VM (like EC2)
        # - Anand M 9/20 
        #input_choice=st.sidebar.radio("# :blue[Choose the Input Method]",('Document','Weblink','YouTube','Audio','Image','PPT'))
        input_choice=st.sidebar.radio("# :blue[Choose the Input Method]",('Document','Weblink','Audio','Image','PPT'))
        if input_choice=="Document":
            with st.sidebar.expander("📁 __Documents__",expanded=True):
                uploaded=st.file_uploader(label="Select File",type=['pdf','txt'],on_change=clear)
        elif input_choice=="Weblink":
            with st.sidebar.expander("🌐 __Webpage__",expanded=True):
                uploaded=st.text_input('Enter a weblink',on_change=clear)
        elif input_choice=="Audio":
            with st.sidebar.expander("🎙 __Audio__",expanded=True):
                uploaded=st.file_uploader('Select File',type=['mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav'],on_change=clear)
        elif input_choice=="Image":
            with st.sidebar.expander("🎙 __Text from Image__",expanded=True):
                uploaded=st.file_uploader('Select File',type=['jpg','jpeg','png'],on_change=clear, disabled=False)
                if uploaded:
                    image=Image.open(uploaded)
                    loc='./Assets/'+str(uploaded.name)
                    image.save(loc)
        elif input_choice=="PPT":
             with st.sidebar.expander("🖼️ __Powerpoint__",expanded=True):
                 uploaded = st.file_uploader("Select your PPT", type=['ppt', 'pptx'], accept_multiple_files=False) 
             

                 
        
        return input_choice, uploaded

# function to display document input options and return the input choice and uploaded file
# this function is called from the main.py file
def select_models(page):
     with st.sidebar:
        llm_model_name = st.selectbox("# :blue[Select LLM Model]", options=MODELS_LLM.keys())
        emb_model_name = st.selectbox("# :blue[Select Embedding Model]", options=MODELS_EMB.keys())
        if page == "rag":
            retriever = st.selectbox("# :blue[Select Retriever]", options=["Opensearch","Kendra"])
            if "OpenSearch" in retriever:
                K=st.slider('Top K', min_value=0., max_value=10., value=1., step=1.)
                engine=st.selectbox('KNN algorithm', ("nmslib", "lucene"), help="Underlying KNN algorithm implementation to use for powering the KNN search")
                m=st.slider('Neighbouring Points', min_value=16.0, max_value=124.0, value=72.0, step=1., help="Explored neighbors count")
                ef_search=st.slider('efSearch', min_value=10.0, max_value=2000.0, value=1000.0, step=10., help="Exploration Factor")
                ef_construction=st.slider('efConstruction', min_value=100.0, max_value=2000.0, value=1000.0, step=10., help="Explain Factor Construction")            
                chunk=st.slider('Token Chunk size', min_value=100.0, max_value=5000.0, value=1000.0, step=100.,help="Token size to chunk documents into Vector DB")

        st.header(":blue[Inference Parameters]")  
        max_len = st.slider('Max Length', min_value=50, max_value=2000, value=300, step=10)
        top_p = st.slider('Top p', min_value=0., max_value=1., value=1., step=.01)
        temp = st.slider('Temperature', min_value=0., max_value=1., value=0.01, step=.01)
        
        if page == "rag" and "OpenSearch" in retriever:
            params = {'action_name':'Document Quer', 'endpoint-llm':MODELS_LLM[llm_model_name],'max_len':max_len, 'top_p':top_p, 'temp':temp, 
                      'model_name':llm_model_name, "emb_model":MODELS_EMB[emb_model_name], "rag":retriever,"K":K, "engine":engine, "m":m,
                     "ef_search":ef_search, "ef_construction":ef_construction, "chunk":chunk, "domain":st.session_state['domain'],'Bucket': BUCKET,'Prefix': PREFIX,'Region_Name': REGION}
        elif page == "rag" and "Kendra" in retriever:
            params = {'model_name': llm_model_name, 'endpoint-llm':MODELS_LLM[llm_model_name], "emb_model":emb_model_name, 'endpoint-emb': MODELS_EMB[emb_model_name],'max_len':max_len, 'top_p':top_p, 'temp':temp,'action_name': "Document Query",'Bucket': BUCKET,'Prefix': PREFIX,"rag":retriever,'Region_Name': REGION}
        else:
            params = {'model_name': llm_model_name, 'endpoint-llm':MODELS_LLM[llm_model_name], "emb_model":emb_model_name, 'endpoint-emb': MODELS_EMB[emb_model_name],'max_len':max_len, 'top_p':top_p, 'temp':temp,'action_name': "Document Query",'Bucket': BUCKET,'Prefix': PREFIX,"rag":"",'Region_Name': REGION}
            
            
     return params

# display function for the first column of the app homepage and info page
# this function is called from the main.py file
def first_column():
            st.markdown("<p style='text-align:center; color:blue;'><u><b>About Me</b></u></p>",unsafe_allow_html=True)
            st.markdown("<p style='color:#FFFFFF;'>🤝 This is an QnA agent, based on RAG (Retrieval Augmented Generation Architecture) that answers questions by reading assets (like documents, Power point slides, videos & audios) provided by you.</p>",unsafe_allow_html=True)
            st.write(" ")
            st.write(" ")
            st.write(" ")            
            st.markdown("<span style='color:#FFFFFF;'>🤝 This system is built on [Streamlit](https://streamlit.io/) using [Amazon Bedrock](https://aws.amazon.com/bedrock/) powered large language models and a diverse set of document loaders developed by [LangChain](https://python.langchain.com/en/latest/index.html). Also [FAISS](https://python.langchain.com/docs/integrations/vectorstores/faiss/) is used as in-memory Vector store.</span>", unsafe_allow_html=True)
            st.write(" ")
            st.write(" ")
            st.markdown("<p style='color:#FFFFFF;'>🤝 Wide ranges of input choices available viz. Documents(.pdf and .txt), web ulrs(single page), YouTube links, Audio files and text from Images and Power Points are enabled. Websites with embedded links and Heavy Spreadsheets are in the upcoming versions.</p>", unsafe_allow_html=True)
            st.write(" ")        
            st.write(" ")


# display function for the second column of the app homepage and info page
# this function is called from the main.py file
def second_column():
            st.write(" ")
            st.write(" ")
            st.write(" ")
            st.markdown("<span style='color:#FFFFFF;'>👉🏽 You can then choose the asset you want to chat on. From the radio buttons on the sidebar. Presently you can select 📜 documents or 🔗 links to webpages, videos, images basis your choice.",unsafe_allow_html=True)
            st.write(" ")
            st.write(" ")

# display function for the second column of the app homepage and info page
# this function is called from the main.py file
def third_column():
            st.write(" ")
            st.write(" ")
            st.markdown("""<span style='color:#FFFFFF;'>The Reference for this project are as follows <br>
            <ul>
                <li><a href="https://aws.amazon.com/blogs/machine-learning/build-a-conversational-chatbot-using-different-llms-within-single-interface-part-1/">Build a conversational chatbot using different LLMs within single interface – Part 1</a> </li>
                <li><a href="https://medium.com/@e-miguel/deploy-a-dynamic-website-on-aws-with-cloudformation-235e1e6a84a7">Deploy a Dynamic Website on AWS with CloudFormation</a> </li>
                <li><a href="https://alledevops.com/building-a-secure-and-scalable-django-blog-on-aws-the-ultimate-guide">Building a Secure and Scalable Django Blog on AWS: The Ultimate Guide</a> </li>
                <li><a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/Welcome.html">AWS CloudFormation User Guide </a> </li>
            </ul>
            </span>""",unsafe_allow_html=True)
            st.write(" ")
            st.write(" ")
            st.markdown("""<span style='color:#FFFFFF;'> The Code for this project can be found here - <a href="https://github.com/zaskap/rag_chatbot_dav_6300_discussion_2"> Project Github Repo </a></span>""",unsafe_allow_html=True)
            st.write(" ")
            st.write(" ")
            

# display function for the header display
def heads():
    
    st.markdown("<h3 style='text-align:center;'>👋🏽 Hey There! I am <span style='color:#4B91F1'>RAG_Chatbot</span>!⚡</h3>",unsafe_allow_html=True)
    st.markdown("""
    <p style='text-align:center;'>I answer questions after reading documents, webpages, images with text, YouTube videos, audio files and spreadsheets.</span></p>
    """,unsafe_allow_html=True)
    st.markdown("""
    <p style='text-align:center;'> This Project is build for DAV 6300 Course on Cloud Computing - Discussion 2 </span></p>
    """,unsafe_allow_html=True)
    st.markdown("""
    <p style='text-align:center;'> Adapted and Built by <b>Group 4</b><br>
                <ul>
                    <li>Aswin Karthik Panneer Selvam</li>
                    <li>Billy Muchipisi</li>
                    <li>Shaikh Umair Ahmed</li>
                </ul>
    </span></p>
    """,unsafe_allow_html=True)
    st.markdown("<h6 style='text-align:center;'> ✨ You can ask me anything from the uploaded content ✨</h6>",unsafe_allow_html=True)
    

# display function for the contact info
def contact():

    st.markdown("""Made by *Aswin Karthik Panneer Selvam*, *Billy Muchipisi*, *Shaikh Umair Ahmed*
                For DAV 6300 - Discussion 2""", unsafe_allow_html=True)
    st.write(" ")
    st.markdown("""LinkedIn : <br>
                <ul>
                <li><a href="https://www.linkedin.com/in/askap/">Aswin Karthik Panneer Selvam</a></li>
                <li><a href="https://www.linkedin.com/in/billymuchipisi/">Billy Muchipisi</a></li>
                <li><a href="https://www.linkedin.com/in/shaikh-umair-ahmed01/">Shaikh Umair Ahmed</a></li>
                </ul>
                """, unsafe_allow_html=True)
    
    
# function to clear the cache and initialize the chat
def clear(greeting=greeting):
    with st.spinner("Clearing all history..."):
        st.cache_data.clear()
        if 'history' in st.session_state:
            del st.session_state['history']
        if 'pastinp' in st.session_state:
            del st.session_state['pastinp']
        if 'pastresp' in st.session_state:
            del st.session_state['pastresp']
        if 'summary_flag' in st.session_state:
            del st.session_state.summary_flag
        if 'summary_content' in st.session_state:
             del st.session_state.summary_content

        initialize_chat(greeting)


# function to clear the cache and initialize the chat
def clear_new():
    with st.spinner("Clearing all history..."):
        st.cache_data.clear()
        if 'generated' in st.session_state:
            del st.session_state['generated']
        if 'past' in st.session_state:
            del st.session_state['past']
        if 'messages' in st.session_state:
            del st.session_state['messages']
        if 'domain' not in st.session_state:
            st.session_state['domain'] = 1

        initialize_chat(greeting)        

# This function for writing chat history into a string variable called hst
# This function is called from the main.py file
# This function is called when the user clicks on the download button
def write_history_to_a_file():
    hst=""
    st.session_state['history']=[]
    st.session_state['history'].append("RAG_Chatbot says -")
    st.session_state['history'].append(st.session_state['pastresp'][0])
    for i in range(1,len(st.session_state['pastresp'])):
        st.session_state['history'].append("Your Query - ")
        st.session_state['history'].append(st.session_state['pastinp'][i-1])
        st.session_state['history'].append("RAG_Chatbot's response - ")
        st.session_state['history'].append(st.session_state['pastresp'][i])

    for item in st.session_state['history']:
        hst+="\n"+str(item)
    
    return hst

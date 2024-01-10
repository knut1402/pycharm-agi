###### GPT

import os

'''need to manually dl certificates! I was able to resolve this issue at my end by following below steps:
1. Visit https://api.openai.com/v1/engines 300 from the browser and cancel the password prompt
2. Click on the lock icon on near the browser url to get the certificate info
3. Depending on your browser find the certificate details and download the root certificate file. For chrome click on connection is secure → Certificate is valid → Details tab and select the top most certificate and click export.
4. Once downloaded move it to the folder where you need it stored
5. Add the below code in your main app code to set the environment variable pointing to this certificate we downloaded
os.environ['REQUESTS_CA_BUNDLE'] = '/path/to/certificate.crt'
'''

os.environ['REQUESTS_CA_BUNDLE'] = "C:/Users/A00007579/OneDrive - Allianz Global Investors/Documents/Python archive/DataLake/GPT/agi_CA.crt"

import openai
openai.organization = "org-lHN2LTqx2aorMO6YwLsZHVbM"
openai.api_key = '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'
models = openai.Model.list()

data = pd.DataFrame(models["data"])
data.head(20)


#### code generation
# generate code from text
prompt_text = """ Write a Python function that accepts first name, second name, 
and birth date in string format as a parameter values
and returns the full name, and the number of days from the birth date to today """

response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  prompt= prompt_text,
  temperature=0,
  max_tokens=256,
)

for choice in response['choices']:
    print(choice['text'])


###### GPT 3.5T

completion = openai.ChatCompletion.create(
  model="gpt-3.5-turbo", 
  messages = [{"role": "system", "content" : "You are ChatGPT, a large language model trained by OpenAI."},
{"role": "user", "content" : "How are you?"},
{"role": "assistant", "content" : "I am doing well"},
{"role": "user", "content" : "In the context of financial data, what is a medusa chart? Think of forecast/expected results vs actual outcomes as several time series - with forecast being updated over time until actual outcome. Can you try to produce an example?"}]
)

for choice in completion['choices']:
    print(choice['message']['content'])


###### LangChain

import langchain
langchain.agents.get_all_tool_names()
from langchain.agents import create_pandas_dataframe_agent
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain.llms import OpenAI
os.environ["OPENAI_API_KEY"] = "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"

#df = pd.read_pickle('./DataLake/USD_SW.pkl')
#agent = create_pandas_dataframe_agent(OpenAI(temperature=0), df, verbose=True)
#agent.run("summarise the dataframe in words?")

data = pd.ExcelFile("./DataLake/eco_master.xlsx")
data_df = pd.read_excel(data,"EcoData")
us = get_data(data_df, 'US', '20000101', end=-1, cat1='all', cat2='all', change=6, roc =3, zs_period = 3)

#old
agent1 = create_pandas_dataframe_agent(OpenAI(temperature=0), us.df_pct, verbose=True, max_iterations=1000)
#with functions
agent2 = create_pandas_dataframe_agent( ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613"), us.df_pct, verbose=True, agent_type=AgentType.OPENAI_FUNCTIONS)

agent.run("what is the median JOLTS when Philly Fed < 0?")

agent1.run("Build a Hierarchical clustering of the data. Agglomerative. Use: scipy.cluster.hierarchy. use matplotlib.pyplot.show()")

agent.run("Show a heatmap of the data time series")

from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType, Tool, initialize_agent, tool
tools = [
    Tool(
        name = "Randomfx",
        func=cubeit,
        description="random function to sqaure number"
    )
]

def cubeit(x):
    return x**2

agent.run("Calculate the results of running function Randomfx on Ind Prod. Show results in a dataframe. Save results locally")


os.getcwd()





d1 = build_vol_surf(['TYM3C 115'], chain_len=[2,2], b=0)
d1.tab.columns

o1 = []
for i in np.arange(len(d1.tab)):
    if d1.tab['opt_type'][i] > 0:
        o1.append('Call')
    else:
        o1.append('Put')

d1.tab['option_type'] = o1
d1.tab['option_price'] = d1.tab['px']


agent = create_pandas_dataframe_agent(OpenAI(temperature=0), d1.tab, verbose=True, max_iterations=25)
agent.run("For opt_type = 1, what is the difference in option price and delta between the 115 and 116 call?")
agent.run("For opt_type = 1,get the option prices for the 113.5, 114.5, 115.5 calls. Dot product them with the array [1,-2, 1]?")


tool_names = ['wikipedia']
llm = OpenAI(temperature=0)
tools = load_tools(tool_names, llm=llm)
agent = create_pandas_dataframe_agent(llm, d1.tab, verbose=True, max_iterations=25, prefix = '\nYou are working with a pandas dataframe in Python. The name of the dataframe is `df`.\nYou should use the tools below to answer the question posed of you: wikipedia')
agent.run("For opt_type = 1, what is the option price and delta of the 115 call?")






### pdf reader

import langchain
import os
import openai
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain import OpenAI, VectorDBQA
from langchain.chains import RetrievalQA
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.chat_models import ChatOpenAI
os.environ["OPENAI_API_KEY"] = "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"
import nltk

nltk.download("punkt")


#### load pdf
loader = UnstructuredFileLoader("./DataLake/mankiw.pdf", mode = 'elements')
documents= loader.load()

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings(openai_api_key = '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')
doc_search = Chroma.from_documents(texts,embeddings)
chain = VectorDBQA.from_chain_type(llm=OpenAI(), chain_type="stuff", vectorstore=doc_search)



start_time = time.time()
loader = UnstructuredFileLoader("./DataLake/barcap_grw_200423.pdf", mode = 'elements')
documents= loader.load()
print("--- %s seconds ---" % (time.time() - start_time))







from langchain.document_loaders import PyPDFLoader
loader = PyPDFLoader("./DataLake/barcap_grw_200423.pdf")
pages = loader.load_and_split()
pages[0]

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(pages)
texts[0]

embeddings = OpenAIEmbeddings(openai_api_key = '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')
#embeddings = OpenAIEmbeddings()
doc_search = Chroma.from_documents(texts,embeddings)

qa = RetrievalQA.from_chain_type(llm=ChatOpenAI(model='gpt-4'), chain_type="stuff", retriever=doc_search.as_retriever(),  return_source_documents=True)
query = "What are the trade recommendations?"
result = qa({"query": query})

result["result"]
result["source_documents"]


import pinecone as pn
from langchain.vectorstores import pinecone
os.environ['REQUESTS_CA_BUNDLE'] = "C:/Users/A00007579/OneDrive - Allianz Global Investors/Documents/Python archive/DataLake/GPT/aws_pinecone.crt"


pn.init(api_key="ca26a22e-012b-4c98-8b4b-6ea7eb263f26", environment="us-east-1-aws")
index_name = "barc-test"
index = pn.Index(index_name)
index.describe_index_stats()

doc_store = langchain.vectorstores.Pinecone.from_texts([d.page_content for d in texts ], embeddings, index_name=index_name)


import ssl
print(ssl.get_default_verify_paths().openssl_cafile)

import requests as r
print(r.certs.where())

import certifi
os.environ['REQUESTS_CA_BUNDLE'] = os.path.join(os.path.dirname(sys.argv[0]), certifi.where())



#################### multiple pdfs
from langchain.document_loaders import DirectoryLoader
loader_both = DirectoryLoader('./DataLake/pdf/', glob="**/*.pdf", loader_cls=PyPDFLoader)
docs_both = loader.load_and_split()
len(docs_both)

comb_text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
comb_texts = comb_text_splitter.split_documents(docs_both)
comb_texts[0]

embeddings = OpenAIEmbeddings(openai_api_key = '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')
comb_doc_search = Chroma.from_documents(comb_texts,embeddings)

comb_qa = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="map_reduce", retriever=comb_doc_search.as_retriever(),  return_source_documents=True)
comb_query = "What are JP Morgan's trade recommendation for 1. UK, GBP, Sonia, UKT, Gilts and RPI?"
comb_query = "What are JP Morgan's trade recommendation for US rates?"
comb_result = comb_qa({"query": comb_query})

comb_result["result"]
comb_result["source_documents"]

comb_qa_ref = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="refine", retriever=comb_doc_search.as_retriever(),  return_source_documents=True)
comb_query = "What are JP Morgan's trade recommendation for 1. UK, GBP, Sonia, UKT, Gilts and RPI?"
comb_query = "What are JP Morgan's trade recommendation for US rates?"
comb_result_ref = comb_qa_ref({"query": comb_query})

comb_result_ref["result"]
comb_result_ref["source_documents"]


comb_qa_mrr = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="map_rerank", retriever=comb_doc_search.as_retriever(),  return_source_documents=True)
comb_query = "What are JP Morgan's trade recommendation for 1. UK, GBP, Sonia, UKT, Gilts and RPI?"
comb_result_mrr = comb_qa_mrr({"query": comb_query})

comb_result_mrr["result"]
comb_result_ref["source_documents"]




comb_qa_refine = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="refine", retriever=comb_doc_search.as_retriever())
comb_query_refine = "What are JP Morgan's trade recommendation for 1. UK, GBP, Sonia, UKT, Gilts and RPI?"
comb_qa_refine.run(comb_query_refine)

comb_qa_mrr2 = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="map_rerank", retriever=comb_doc_search.as_retriever())
comb_query = "What are JP Morgan's trade recommendation in US rates?"
comb_qa_mrr2.run(comb_query)









############### back to single

jpm_load = PyPDFLoader("./DataLake/pdf/jpm_gfi_220423.pdf")
jpm_pages = jpm_load.load_and_split()
jpm_pages[0]

jpm_text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
jpm_texts = text_splitter.split_documents(jpm_pages)
jpm_texts[0]

embeddings = OpenAIEmbeddings(openai_api_key = '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')
jpm_search = Chroma.from_documents(jpm_texts,embeddings)

jpm_qa_st = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="stuff", retriever=jpm_search.as_retriever(),  return_source_documents=True)
jpm_qa_mr = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="map_reduce", retriever=jpm_search.as_retriever(),  return_source_documents=True)
jpm_qa_ref = RetrievalQA.from_chain_type(llm=OpenAI(), chain_type="refine", retriever=jpm_search.as_retriever(),  return_source_documents=True)

query = "What are JP Morgan's trade recommendation for 1. UK, GBP, Sonia, UKT, Gilts and RPI?"
query = "What are JP Morgan's trade recommendation for USD rates?"

result_st = jpm_qa_st({"query": query})
result_st["result"]

result_mr = jpm_qa_mr({"query": query})
result_ref = jpm_qa_ref({"query": query})
result_mr["result"]
result_ref["result"]
















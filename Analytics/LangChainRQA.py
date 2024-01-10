#### testing diff retrieval capabilities
import os

import openai
import pandas as pd

openai.organization = "org-lHN2LTqx2aorMO6YwLsZHVbM"
openai.api_key = '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'
#models = openai.Model.list()
#data = pd.DataFrame(models["data"])
#data.head(20)


import langchain
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain import OpenAI
from langchain.chains import LLMChain
from langchain.chains import RetrievalQA
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import DirectoryLoader
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.question_answering import load_qa_chain
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from langchain.memory import ConversationBufferMemory
import nltk

os.environ["OPENAI_API_KEY"] = "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"


##### individual pdfs load
pdf_list = ['citi_erw_200423', 'barcap_grw_200423', 'jpm_gfi_220423']

loader = [PyPDFLoader("./DataLake/pdf/"+i+".pdf") for i in pdf_list]
get_pages = [loader[i].load_and_split() for i in np.arange(len(pdf_list))]
#get_pages[0][0]
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
get_texts = [text_splitter.split_documents(get_pages[i]) for i in np.arange(len(pdf_list))]
#get_texts[0][0]

embeddings = OpenAIEmbeddings(openai_api_key = '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')
doc_search = [Chroma.from_documents(get_texts[i],embeddings) for i in np.arange(len(pdf_list))]


#### retrieval_qa
queries = ['What is the forecast for terminal ECB rate?',
           'What are the trade recommendations for UK, GBP, Sonia, UKT, Gilt, RPI?',
           'Describe what is represented in Figure 1.',
           'What are the trade recommendation in inflation?']
retriever_search_types = ['similarity','mmr']
chain_types = ['stuff','map_reduce','refine','map_rerank']

answers = []
for i in np.arange(len(pdf_list)):
    for j in retriever_search_types:
        for k in chain_types:
            try:
                qa = RetrievalQA.from_chain_type(
                    llm=OpenAI(temperature=0, openai_api_key = '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'),
                    chain_type=k,
                    retriever=doc_search[i].as_retriever(search_type=j),
                    return_source_documents=True)

                for m in np.arange(len(queries)):
                    print(pdf_list[i], j, k)
                    print(queries[m])
                    result = qa({"query": queries[m]})
#                    print(result["result"])
                    answers += [[pdf_list[i], j, k, queries[m], result["result"]]]

            except:
                answers += [[pdf_list[i], j, k, queries[m], "Missing"]]
                pass

answers
c1 = ['pdf', 'rs', 'ct', 'query', 'ans']
df1 = pd.DataFrame(answers, columns=c1)

df2 = df1[df1['pdf'] == pdf_list[0]]
df3 = df2[df2['query'] == queries[2]]

[print(df3['rs'].iloc[i], df3['ct'].iloc[i], ': ',df3['ans'].iloc[i]) for i in np.arange(len(df3))]


###### combined pdfs
loader = DirectoryLoader('./DataLake/pdf/', glob="**/*.pdf", loader_cls=PyPDFLoader)
all_pages = loader.load_and_split()
#len(all_pages)
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
all_texts = text_splitter.split_documents(all_pages)

embeddings = OpenAIEmbeddings(openai_api_key = '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')
docs_search = Chroma.from_documents(all_texts,embeddings)

#### retrieval_qa
queries = ['What is the forecast for terminal ECB rate?',
           'What are the trade recommendations for UK, GBP, Sonia, UKT, Gilt, RPI?',
           'Describe what is represented in Figure 1.',
           'What are the trade recommendation in inflation?']
retriever_search_types = ['similarity','mmr']
chain_types = ['stuff','map_reduce','refine','map_rerank']

answers_all = []
for j in retriever_search_types:
    for k in chain_types:
        try:
            qa = RetrievalQA.from_chain_type(
                llm=OpenAI(temperature=0, openai_api_key = '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'),
                chain_type=k,
                retriever=docs_search.as_retriever(search_type=j),
                return_source_documents=True)

            for m in np.arange(len(queries)):
                print("All", j, k)
                print(queries[m])
                result = qa({"query": queries[m]})
                answers_all += [["All", j, k, queries[m], result["result"]]]

        except:
            answers_all += [["All", j, k, queries[m], "Missing"]]
            pass

##### Applying conversational chain
llm = OpenAI(temperature=0, openai_api_key = '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')
q_gen = LLMChain(llm=llm, prompt=CONDENSE_QUESTION_PROMPT)
doc_chain = load_qa_chain(llm, chain_type="refine")
#hist = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

CQA = ConversationalRetrievalChain(
    retriever=docs_search.as_retriever(),
    question_generator=q_gen,
    combine_docs_chain=doc_chain)

chat_history = []
query = "What are the trades in inflation?"
result = CQA({"question": query, "chat_history": chat_history})
result["answer"]

chat_history = [(query, result["answer"])]
query = "What does JP Morgan recommend?"
result = CQA({"question": query, "chat_history": chat_history})
result["answer"]





















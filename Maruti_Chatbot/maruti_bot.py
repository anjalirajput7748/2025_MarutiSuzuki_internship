import os
import streamlit as st
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA

from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint


DB_FAISS_PATH="vectorstore/db_faiss"
@st.cache_resource
def get_vectorstore():
    embedding_model=HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    db=FAISS.load_local(DB_FAISS_PATH,embedding_model,allow_dangerous_deserialization=True)
    return db

def set_custom_prompt(custom_prompt_template):
    prompt=PromptTemplate(template=custom_prompt_template,input_variables=["context","question"])
    return prompt

from langchain_community.llms import Ollama
llm =Ollama(model="gemma2:2b",temperature=0.5)
print(llm)


def main():
    st.title("  Ask Chatbot!")

    if'messages' not in st.session_state:
        st.session_state.messages =[]

    for message in st.session_state.messages:
        st.chat_message(message['role']).markdown(message['content'])


    prompt = st.chat_input("Pass your prompt here")

    if prompt:
        st.chat_message('user').markdown(prompt)
        st.session_state.messages.append({'role':'user','content': prompt})

        CUSTOM_PROMPT_TEMPLATE = """
                Use the pieces of information provided in the context to answer user's question.
                If you dont know the answer, just say that you dont know, dont try to make up an answer.
                give some Creative answer from the given documents.
                Don't provide the document's address just provide the correct answer 

                Context:{context}
                Question:{question}

                 Start the answer directly.
                """
        try:
            # Load vectorstore
            vectorstore = get_vectorstore()
            if vectorstore is None:
                st.error("Failed to load the vector store")
                return

            # Define qa_chain
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True,
                chain_type_kwargs={"prompt": set_custom_prompt(CUSTOM_PROMPT_TEMPLATE)}
            )

            # Call the chain
            response = qa_chain.invoke({'query': prompt})
            import os

            result = response["result"]
            source_documents = response["source_documents"]

# Format source info: only file name and page number
            formatted_sources = []
            for doc in source_documents:
             source_path = doc.metadata.get("source", "Unknown source")
             source_file = os.path.basename(source_path)
             page = doc.metadata.get("page", "Unknown page")
             formatted_sources.append(f"- {source_file} (Page {page})")

# Combine result and formatted source info
             result_to_show = result + "\n\n**Sources:**\n" + "\n".join(formatted_sources)

# Display in Streamlit chat
            st.chat_message('assistant').markdown(result_to_show)
            st.session_state.messages.append({'role': 'assistant', 'content': result_to_show})


            
        except Exception as e:
            st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
    


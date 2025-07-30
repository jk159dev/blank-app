import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

import time

from utils import *


# import transformers

# tokenizer = transformers.AutoTokenizer.from_pretrained("maritaca-ai/sabia-2-tokenizer-medium")

# def count_tokens(prompt):
#     # prompt = debug_prompt_list_criterion_full[0][0]
#     tokens = tokenizer.encode(prompt)
#     # print(f'O prompt "{prompt}" contém {len(tokens)} tokens.')  # It should print 12 tokens.
#     # print( len(prompt.split()) )
#     return [ len(prompt.split()), len(tokens) ]

# def number_tokens_words( debug_prompt_list_criterion_full, prompt_criterion ):
#     number_tokens = 0
#     numer_words = 0
#     for i in range( len(debug_prompt_list_criterion_full) ):
#         for j in range(len(debug_prompt_list_criterion_full[i])):
#             number_tokens += count_tokens( debug_prompt_list_criterion_full[i][j] )[1]
#             numer_words += count_tokens( debug_prompt_list_criterion_full[i][j] )[0]
    
#     number_tokens += count_tokens( prompt_criterion )[1]
#     numer_words += count_tokens( prompt_criterion )[0]
    
#     print( f"""number_tokens: {number_tokens}, number_words: {numer_words}""" )

import maritalk

from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables from the .env file
load_dotenv()

model = maritalk.MariTalk(
    key=os.getenv('API_KEY'),
    model=os.getenv('MODEL')  # No momento, suportamos os modelos sabia-3, sabia-2-medium e sabia-2-small
)

# Initialize the list if it doesn't exist
if 'list_files' not in st.session_state:
    st.session_state.list_files = []

description = """Título do Projeto, Objetivo do Projeto, Introdução, Justificativa, Revisão da Literatura,
                Metodologia, Cronograma, Orçamento, Resultados Esperados, Impacto Potencial, Referências,"""

st.title("Demo App")
st.write("Este aplicativo realiza a avaliação automática de documentos e oferece sugestões personalizadas para aprimoramento.")
st.write("Você pode fazer upload de um arquivo .txt com a seguinte estrutura:")
st.write(description)
st.markdown("[Baixar arquivo de exemplo](https://bit.ly/template_projeto2024)")

uploaded_file = st.file_uploader("Escolher arquivo", type=["txt"])

import numpy as np
import matplotlib.pyplot as plt

@st.cache
def processing(criterion, _model, project_dict):

    # Processar todos os critérios
    for criterion in criterions:
        idxs_criterion = criterion['idxs']
        prefix_criterion = criterion['criterion']
        prompt_list_subcriterion = criterion['subcriterion']
        
        # Criando os prompts e obtendo as respostas
        prompt_list_criterion_full, all_responses = create_full_prompt_and_get_responses(
            model, project_dict, prompt_list_subcriterion, idxs_criterion, prefix, posfix
        )

        score = f""" Avalie o seguinte projeto utilizando a escala de pontuações de 0 a 5, onde 0 é o pior resultado possível e 5 é o melhor resultado possível. Assegure-se de que sua resposta seja composta exclusivamente pelas pontuações atribuídas, sem quaisquer comentários ou explicações. Baseie-se nas seguintes {len(prompt_list_subcriterion)} subavaliações: """
        # Criando o prompt final com base nas respostas
        prompt_criterion = create_prompt_based_on_responses_of_questions_for_criterion(all_responses, prefix_criterion, score)
        
        # Obtendo as pontuações das respostas
        criterion_responses_values = get_score_from_responses_of_question(model, prompt_criterion)

        # Armazenando os resultados de depuração
        debug_all_responses.append(all_responses)
        debug_prompt_list_criterion_full.append(prompt_list_criterion_full)
        debug_criterion_responses_values.append(criterion_responses_values)

    return debug_criterion_responses_values

if uploaded_file is not None:
    print(uploaded_file)

    file_content = uploaded_file.read().decode("utf-8")#.splitlines()

    project_dict = file2dict(file_content)

    st.write("File successfully uploaded and read!")

    filename = os.path.splitext(uploaded_file.name)[0]
    new_filename = blablabla(filename, file_content)

    st.session_state.list_files.append(new_filename)

    print( st.session_state.list_files )

    # st.write("File content:")
    # st.write(project_dict)


    # Inicializando as variáveis de depuração fora do loop
    debug_all_responses = []
    debug_prompt_list_criterion_full = []
    debug_criterion_responses_values = []

    # Definindo as funções fora do loop, caso ainda não estejam definidas

    start = time.time()

    debug_criterion_responses_values = processing(criterions, model, project_dict)

    end = time.time()
    st.write(f'Time seconds: {end-start}')

    # Chamando a função para cada lista de respostas
    print_media(debug_criterion_responses_values[0], "Critério 1")
    print_media(debug_criterion_responses_values[1], "Critério 3")
    print_media(debug_criterion_responses_values[2], "Critério 4")
    print_media(debug_criterion_responses_values[3], "Critério 5")

    st.subheader('Data Visualization')

    # Calculate the mean of each sublist
    means = [np.mean(sublist) for sublist in debug_criterion_responses_values]

    # Define x labels
    x_labels = [f'Criterion{i+1}' for i in range(len(means))]

    # Create the bar plot using matplotlib
    fig, ax = plt.subplots(figsize=(7, 3))

    ax.bar(x_labels, means)

    # Set x and y labels
    ax.set_xlabel('Criterion')
    ax.set_ylabel('Score')
    ax.set_title('Mean Scores per Criterion')

    # Display the plot in Streamlit
    st.pyplot(fig)
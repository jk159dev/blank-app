from datetime import datetime
import streamlit as st
import os

strings_to_search = ["Título do Projeto:",
                    "Objetivo do Projeto:",
                    "Introdução:",
                    "Justificativa:",
                    "Revisão da Literatura:",
                    "Metodologia:",
                    "Cronograma:",
                    "Orçamento:",
                    "Resultados Esperados:",
                    "Impacto Potencial:",
                    "Referências:", ]

def file2dict(project_text):
    project_dict = {}
    
    # project_text = list_projects[0]
    
    for i in range( len(strings_to_search) - 1 ):
        idx = project_text.find(strings_to_search[i])
        idx1 = project_text.find(strings_to_search[i+1])
        # print( project_text[idx+len(strings_to_search[i]):idx1] )
        project_dict[strings_to_search[i]] = project_text[idx+len(strings_to_search[i]):idx1]
    
    last_string = strings_to_search[ len(strings_to_search)-1 ]
    idx = project_text.find( strings_to_search[ len(strings_to_search)-1 ] )
    project_dict[last_string] = project_text[idx:]
    
    return project_dict

# Função para realizar a geração de respostas
def gerar_respostas(model, prompt, quantidade):
    respostas = []
    for _ in range(quantidade):
        response = model.generate(prompt)
        respostas.append(response["answer"])
    return respostas

def get_values( scores_string ):
    # Remove espaços em branco e divide a string em substrings usando a vírgula como separador
    numeros_str_list = scores_string.replace(' ', '').split(',')
    # Converte as substrings em inteiros e retorna a lista de números
    return [int(num) for num in numeros_str_list]

def create_prompt_based_on_questions_for_criterion( project_dict, prompt_list_criterion_1, idxs_criterion_1, prefix, posfix ):
    prompt_list_criterion_1_full = []

    for i in range( len(idxs_criterion_1) ):
        line = f'{prefix}{prompt_list_criterion_1[i]}, o texto é o seguinte [{project_dict[strings_to_search[idxs_criterion_1[i]]]}] {posfix}'
        # print( f'{line}')
        prompt_list_criterion_1_full.append( line )
        # print( '---'*10 )

    return prompt_list_criterion_1_full

def get_answers_for_prompt_based_on_question_for_criterion( model, prompt_list_criterion_1_full ):
    all_responses = []
    for i in range( len(prompt_list_criterion_1_full) ):
        criterion_responses = gerar_respostas(model, prompt_list_criterion_1_full[i], 1)
        all_responses.append(criterion_responses)
    return all_responses

def create_prompt_based_on_responses_of_questions_for_criterion( all_responses, prefix1, score ):
    prompt_criterion_1 = prefix + prefix1 + score
    # print( prefix + prefix1 + score)
    for i in range( len(all_responses) ):
        line = f'{i+1}. **{all_responses[i][0]}**'
        # print( f'{line}' )
        prompt_criterion_1 += line
    
    # posfix_prompt = """Por favor, atribua uma pontuação de 0 a 5 para cada uma das subavaliações acima, só seguindo o formato abaixo:
    
    # x, y, z"""
    
    prompt_criterion_1 = prompt_criterion_1 + posfix_prompt

    return prompt_criterion_1

def get_score_from_responses_of_question( model, prompt_criterion_1 ) :
    
    criterion_responses_1 = gerar_respostas(model, prompt_criterion_1, 1)
    print( criterion_responses_1, end=', ' )

    # attempts = 0

    if criterion_responses_1[0].find('Peço desculpas pela confusão anterior') == -1:
    
        criterion_responses_1_values = get_values( criterion_responses_1[0] )
        print( criterion_responses_1_values )

        return criterion_responses_1_values
        

    else:
        print('Error')
        criterion_responses_1 = gerar_respostas(model, prompt_criterion_1, 1)
        print( criterion_responses_1, end=', ' )

        criterion_responses_1_values = get_values( criterion_responses_1[0] )
        print( criterion_responses_1_values )
    
        return criterion_responses_1_values

# Definindo as funções fora do loop, caso ainda não estejam definidas
def create_full_prompt_and_get_responses(model, project_dict, subcriterion, idxs, prefix, posfix, response_activated=True):
    prompt_list_full = create_prompt_based_on_questions_for_criterion(project_dict, subcriterion, idxs, prefix, posfix)
    
    all_responses = get_answers_for_prompt_based_on_question_for_criterion(model, prompt_list_full)
    return prompt_list_full, all_responses

def process_criterion(criterion, score):
    idxs_criterion = criterion['idxs']
    prefix_criterion = criterion['criterion']
    prompt_list_subcriterion = criterion['subcriterion']
    
    prompt_list_criterion_full, all_responses = create_full_prompt_and_get_responses(
        project_dict, prompt_list_subcriterion, idxs_criterion, prefix, posfix
    )
    prompt_criterion = create_prompt_based_on_responses_of_questions_for_criterion(all_responses, prefix_criterion, score)
    criterion_responses_values = get_score_from_responses_of_question(prompt_criterion)
    
    return all_responses, prompt_list_criterion_full, criterion_responses_values


def print_media(lista, nome_lista, kind = 0):
    media = sum(lista) / len(lista)
    if kind == 0:
        st.write(f"{nome_lista}: {media:.2f}", end=' ')
    else:
        st.write(f"{nome_lista}: {lista} - Média: {media:.2f}")                        

def blablabla(file_name, file_content):
    # file_name = os.path.splitext(uploaded_file.name)[0]
    
    # Get current UNIX timestamp
    unix_timestamp = int(datetime.now().timestamp())
    
    # Create the new filename with timestamp
    new_filename = f"{file_name}_{unix_timestamp}.txt"
    
    # Define the save path (you can specify your directory here)
    save_path = os.path.join("files", new_filename)
    
    # Save the uploaded file with the new filename
    with open(save_path, "w") as f:
        f.write(file_content)
    
    st.write(f"File saved successfully as {new_filename}!")

    file_size_kb = os.path.getsize(save_path) / 1024
    st.write(f"File size: {file_size_kb:.2f} KB")

    return new_filename


criterions = [
    {
        "criterion": "Avalie a qualidade científica e a relevância do projeto proposto em relação \
        ao estado atual da arte na área. Considere originalidade, inovação e a importância \
        dos objetivos propostos.",
        "idxs": [0, 1, 2, 3, 4, 5],
        "subcriterion": [
                    "Avalie a clareza e concisão do título do projeto. Ele encapsula o foco central da pesquisa?", 
                    
                    "Avalie a definição clara dos objetivos do projeto, as perguntas de pesquisa específicas e os resultados esperados. São relevantes e inovadores?",
                    
                    "Avalie o contexto fornecido na introdução sobre a importância do tema e a relevância científica. As lacunas no conhecimento atual são claramente identificadas?",
                    
                    "Avalie a justificativa do projeto. O argumento é sólido e demonstra a relevância e o potencial impacto do projeto dentro da área de estudo?",
                    
                    "Avalie a revisão da literatura. O resumo das pesquisas anteriores está bem apresentado? As lacunas que o projeto pretende abordar são claramente destacadas?",
                    
                    "Avalie a metodologia descrita. A abordagem metodológica do projeto é adequada e bem detalhada?",
        ]
    },
    {
        "criterion": "Avalie a viabilidade técnica do projeto, incluindo a adequação do cronograma,\
        metodologia e a infraestrutura disponível. Analise também a viabilidade financeira, verificando\
        se o orçamento solicitado é justificado e suficiente.",
        "idxs": [5, 6, 7],
        "subcriterion": [
                    "Avalie o detalhamento do design do estudo, coleta de dados e análise de dados. A metodologia é viável tecnicamente?", 
                    
                    "Avalie o cronograma do projeto. As etapas estão bem delineadas e os prazos são realistas?",
                    
                    "Avalie o orçamento do projeto. A estimativa de custos é detalhada e os recursos solicitados são justificados?",

                    "Avalie a infraestrutura disponível na instituição. Ela é adequada para a execução do projeto?"

        ]
    },
    {
        "criterion": "Considerando os objetivos e resultados esperados, avalie o potencial impacto\
        socioeconômico do projeto. Como os resultados podem contribuir para o desenvolvimento científico,\
        tecnológico, e para a sociedade em geral?",
        "idxs": [8, 9],
        "subcriterion": [
                    "Avalie os resultados específicos que se espera alcançar com a pesquisa. Como eles contribuirão para o campo de estudo?", 
                    
                    "Avalie o impacto científico, tecnológico, social e econômico dos resultados da pesquisa. Quais são as possíveis contribuições para a sociedade?",
                    
        ]
    },
    {
        "criterion": "Avalie o grau de inovação e originalidade do projeto. Em que medida o projeto\
        propõe novas abordagens, métodos ou soluções para problemas existentes na área de estudo?",
        "idxs": [1, 3, 4, 5],
        "subcriterion": [
                    "Avalie a clareza e inovação dos objetivos propostos. Eles trazem algo novo para a área de estudo?", 
                    
                    "Avalie a argumentação sobre a originalidade e inovação do projeto. Como ele se diferencia das pesquisas existentes?",

                    "Avalie a identificação das lacunas no conhecimento atual. As abordagens propostas são inovadoras?",

                    "Avalie a inovação nas abordagens metodológicas propostas. Elas trazem novas soluções para problemas existentes?",
                    
        ]
    }
]


prefix = 'Voce é um especialista em formulaçao de projetos, avaliaçao de projeto com 20 anos de experiencia. E agora está avaliando um projeto. '
posfix = 'Evita incluir sugestões de melhoria. Limita tua resposta a 100 palavras.'
posfix_prompt = """Por favor, atribua uma pontuação de 0 a 5 para cada uma das subavaliações acima, só seguindo o formato abaixo:

x, y, z"""
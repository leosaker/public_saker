import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import warnings
import numpy as np
from reliability.Fitters import Fit_Everything
from reliability.Other_functions import make_right_censored_data

# Função para avaliar a melhor distribuição para uma lista de TTRs
def melhor_distribuicao (Falhas):
    raw_data = list(Falhas)
    data = make_right_censored_data(raw_data, threshold=1500)  # right censor the data
    results = Fit_Everything(failures=data.failures, right_censored = data.right_censored, show_probability_plot = False, 
                             show_histogram_plot=False, show_PP_plot= False, print_results = False
                            , exclude = ['Exponential_2P', 'Gamma_3P', 'Gamma_2P', 'Lognormal_3P', 'Loglogistic_3P','Gumbel_2P'] ) 
    return results.best_distribution_name, results.best_distribution.parameters

# Função para plotar BOXPLOT
def boxplot_TTR(Titulo, Data_Frame,Y, Y_Label):
    st.subheader(Titulo)
    fig = Figure()
    ax = fig.subplots()
    sns.boxplot(x = Data_Frame['TTR (Tempo de reparo)'], y = Data_Frame[Y] , ax=ax, orient='h')
    sns.swarmplot(x = Data_Frame['TTR (Tempo de reparo)'], y = Data_Frame[Y] , ax=ax, color=".25")
    ax.set_ylabel(Y_Label)
    ax.set_xlabel('Duração das Falhas')
    st.pyplot(fig)

# Função para ler o arquivo e guardar no cache    
@st.cache
def load_data():
    dt_UTGCA = pd.read_excel("Acompanhamento Geral de Manutenção RAC _2021.xlsx", sheet_name = "ACOMPANHAMENTO")
    dt_UTGCA = dt_UTGCA[dt_UTGCA['Parada']== 'SIM']
    return dt_UTGCA

dt_UTGCA = load_data()

LISTA_de_equipamentos = sorted(list(dt_UTGCA['Classe Equipamento'].drop_duplicates().dropna()))

st.sidebar.title('UTGCA - Histórico de Falhas')
Equipamento = st.sidebar.selectbox('Selecione um sistema: ',LISTA_de_equipamentos)
st.title('UTGCA - Sistema: '+ Equipamento)

dt_equipamento = dt_UTGCA[dt_UTGCA['Classe Equipamento']== Equipamento]
TAGs = sorted(list(dt_equipamento ['Equipamento afetado'].drop_duplicates().dropna()))

st.subheader("Distribuição dos Tempos de reparo (horas) do sistema:" + Equipamento)
fig = Figure()
ax = fig.subplots()
sns.histplot(dt_equipamento['TTR (Tempo de reparo)'],bins = 10, ax=ax, kde=True)
ax.set_ylabel('Frequência')
ax.set_xlabel('Duração das Falhas')
st.pyplot(fig)


st.subheader("BoxPlot dos tempos de reparo desta classe de equipamentos")
fig = Figure()
ax = fig.subplots()
sns.boxplot(x = dt_equipamento['TTR (Tempo de reparo)'], ax=ax, orient='h')
sns.swarmplot(x = dt_equipamento['TTR (Tempo de reparo)'], ax=ax, color=".25")
ax.set_ylabel(Equipamento)
ax.set_xlabel('Duração das Falhas')
st.pyplot(fig)

boxplot_TTR("BoxPlot dos tempos de reparo de cada equipamento", dt_equipamento,'Equipamento afetado', Equipamento)

boxplot_TTR("BoxPlot dos tempos de reparo das divisões desta classe de equipamentos", dt_equipamento,'Subdivisão', Equipamento)

TAG = st.sidebar.selectbox('Selecione um Equipamento deste sistema:',TAGs)
dt_TAG = dt_equipamento[dt_equipamento['Equipamento afetado']== TAG]

boxplot_TTR("BoxPlot dos tempos de reparo das divisões do equipamento " + TAG, dt_TAG,'Subdivisão', TAG)

classe_Distribuicao, classe_parametros = melhor_distribuicao (dt_equipamento['TTR (Tempo de reparo)'])
TAG_Distribuicao, TAG_parametros = melhor_distribuicao (dt_TAG['TTR (Tempo de reparo)'])

st.subheader("Distribuição Estatística dos tempos de reparo:")

st.write("distribuição da classe - ",Equipamento," : ", classe_Distribuicao)
st.write("Parâmetros da classe - ",Equipamento," : ",classe_parametros)
st.write(" ")
st.write("distribuição do equipamento - ",TAG," : ",TAG_Distribuicao)
st.write("Parâmetros da classe - ",TAG ," : ", TAG_parametros)

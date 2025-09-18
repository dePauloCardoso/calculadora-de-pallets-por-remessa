import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

# Configuração da página
st.set_page_config(
    page_title="Calculadora de Pallets",
    page_icon="📦",
    layout="wide"
)

# Título da aplicação
st.title("📦 Calculadora de Pallets por Remessa")
st.markdown("---")

# Função para carregar a base de dados de produtos
@st.cache_data
def load_product_base():
    """Carrega a base de dados de produtos do arquivo CSV"""
    try:
        # Carrega o arquivo base-dados-produtos.csv
        df_base = pd.read_csv("base-dados-produtos.csv", sep=";")
        
        # Remove linhas com qtd_cx = 0 (produtos sem informação de caixa)
        df_base = df_base[df_base['qtd_cx'] > 0]
        
        # Remove duplicatas mantendo a última ocorrência
        df_base = df_base.drop_duplicates(subset=['item'], keep='last')
        
        return df_base
    except Exception as e:
        st.error(f"Erro ao carregar base de dados: {e}")
        return None

# Função para processar o arquivo do usuário
def process_user_file(uploaded_file):
    """Processa o arquivo CSV enviado pelo usuário"""
    try:
        # Lê o arquivo CSV
        df_pedido = pd.read_csv(uploaded_file)
        
        # Valida se tem as colunas necessárias
        required_columns = ['item', 'qtd']
        if not all(col in df_pedido.columns for col in required_columns):
            st.error(f"O arquivo deve conter as colunas: {required_columns}")
            return None
        
        # Converte qtd para numérico
        df_pedido['qtd'] = pd.to_numeric(df_pedido['qtd'], errors='coerce')
        
        # Remove linhas com qtd inválida
        df_pedido = df_pedido.dropna(subset=['qtd'])
        df_pedido = df_pedido[df_pedido['qtd'] > 0]
        
        return df_pedido
    except Exception as e:
        st.error(f"Erro ao processar arquivo: {e}")
        return None

# Função para calcular volumes e pallets
def calculate_volumes_and_pallets(df_pedido, df_base):
    """Calcula volumes e pallets baseado no pedido e na base de dados"""
    
    # Faz o merge dos dados
    df_resultado = df_pedido.merge(df_base, on='item', how='left')
    
    # Identifica itens não encontrados na base
    itens_nao_encontrados = df_resultado[df_resultado['qtd_cx'].isna()]
    
    # Remove itens não encontrados para o cálculo
    df_calculo = df_resultado.dropna(subset=['qtd_cx'])
    
    if len(df_calculo) == 0:
        return None, itens_nao_encontrados
    
    # Calcula volumes (caixas)
    df_calculo['volumes'] = np.ceil(df_calculo['qtd'] / df_calculo['qtd_cx'])
    
    # Calcula total de volumes
    total_volumes = df_calculo['volumes'].sum()
    
    # Calcula pallets (1 pallet = 48 volumes)
    total_pallets = np.ceil(total_volumes / 48)
    
    return {
        'df_detalhado': df_calculo,
        'total_volumes': int(total_volumes),
        'total_pallets': int(total_pallets),
        'itens_nao_encontrados': itens_nao_encontrados
    }, itens_nao_encontrados

# Interface principal
def main():
    # Carrega a base de dados
    with st.spinner("Carregando base de dados de produtos..."):
        df_base = load_product_base()
    
    if df_base is None:
        st.error("Não foi possível carregar a base de dados. Verifique se o arquivo 'base-dados-produtos.csv' existe.")
        return
    
    st.success(f"✅ Base de dados carregada com {len(df_base)} produtos")
    
    # Upload do arquivo
    st.subheader("📁 Upload do Arquivo de Pedido")
    st.markdown("**Formato esperado:** CSV com colunas 'item' e 'qtd'")
    
    uploaded_file = st.file_uploader(
        "Escolha um arquivo CSV",
        type=['csv'],
        help="O arquivo deve conter as colunas 'item' e 'qtd'"
    )
    
    if uploaded_file is not None:
        # Processa o arquivo
        with st.spinner("Processando arquivo..."):
            df_pedido = process_user_file(uploaded_file)
        
        if df_pedido is not None:
            st.success(f"✅ Arquivo processado com {len(df_pedido)} itens")
            
            # Mostra preview do pedido
            st.subheader("📋 Preview do Pedido")
            st.dataframe(df_pedido.head(10), use_container_width=True)
            
            if len(df_pedido) > 10:
                st.info(f"Mostrando apenas os primeiros 10 itens de {len(df_pedido)} total")
            
            # Calcula volumes e pallets
            with st.spinner("Calculando volumes e pallets..."):
                resultado, itens_nao_encontrados = calculate_volumes_and_pallets(df_pedido, df_base)
            
            if resultado is not None:
                # Exibe resultados principais
                st.subheader("📊 Resultados")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        label="Total de Volumes",
                        value=resultado['total_volumes'],
                        help="Quantidade total de caixas necessárias"
                    )
                
                with col2:
                    st.metric(
                        label="Total de Pallets",
                        value=resultado['total_pallets'],
                        help="1 pallet = 48 volumes"
                    )
                
                with col3:
                    st.metric(
                        label="Itens Processados",
                        value=len(resultado['df_detalhado']),
                        help="Itens encontrados na base de dados"
                    )
                
                # Mostra detalhamento
                st.subheader("📋 Detalhamento por Item")
                df_detalhado = resultado['df_detalhado'].copy()
                df_detalhado = df_detalhado[['item', 'qtd', 'qtd_cx', 'volumes']]
                df_detalhado.columns = ['Item', 'Quantidade Pedida', 'Qtd por Caixa', 'Volumes Necessários']
                df_detalhado['Volumes Necessários'] = df_detalhado['Volumes Necessários'].astype(int)
                
                st.dataframe(df_detalhado, use_container_width=True)
                
                # Botão para download do resultado
                csv_result = df_detalhado.to_csv(index=False, sep=';')
                st.download_button(
                    label="📥 Download do Resultado",
                    data=csv_result,
                    file_name="resultado_calculo_pallets.csv",
                    mime="text/csv"
                )
                
                # Mostra itens não encontrados se houver
                if len(itens_nao_encontrados) > 0:
                    st.warning(f"⚠️ {len(itens_nao_encontrados)} itens não foram encontrados na base de dados:")
                    st.dataframe(itens_nao_encontrados[['item', 'qtd']], use_container_width=True)
            
            else:
                st.error("Nenhum item do pedido foi encontrado na base de dados.")

if __name__ == "__main__":
    main()

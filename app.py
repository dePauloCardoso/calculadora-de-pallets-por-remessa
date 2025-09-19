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

# Explicação da lógica de caixas
with st.expander("ℹ️ Como funciona a seleção de caixas"):
    st.markdown("""
    **Sistema de 3 tipos de caixas:**
    
    - **Caixa Padrão (01)**: Altura completa
    - **Caixa Quebra (02)**: 1/3 da altura da caixa padrão  
    - **Caixa Quebra Menor (03)**: 1/5 da altura da caixa padrão
    
    **Lógica de cálculo:**
    1. **Caixas cheias**: Quando a quantidade ≥ capacidade da caixa
    2. **Caixa quebra**: Para o restante, baseado na porcentagem:
       - **> 50% da capacidade**: Caixa Padrão (01)
       - **30% - 50% da capacidade**: Caixa Quebra (02)
       - **< 30% da capacidade**: Caixa Quebra Menor (03)
    
    **Exemplo**: Pedido de 22 itens, caixa comporta 12
    - 1ª caixa: 12 itens (cheia) = Caixa Padrão (01)
    - 2ª caixa: 10 itens (83%) = Caixa Padrão (01)
    
    **Ocupação no pallet:**
    - 1 pallet = 48 caixas padrão
    - 1 caixa padrão = 3 caixas quebra = 5 caixas quebra menor
    """)

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

# Função para determinar o tipo de caixa baseado na quantidade
def determine_box_type(qtd_pedido, qtd_caixa):
    """Determina o tipo de caixa baseado na quantidade do pedido"""
    if qtd_pedido > qtd_caixa * 1.5:  # > 50% da capacidade
        return "caixa_01", 1  # Caixa padrão
    elif qtd_pedido > qtd_caixa * 1.3:  # Entre 30% e 50%
        return "caixa_02", 1/3  # Caixa quebra (1/3 da altura)
    else:  # < 30%
        return "caixa_03", 1/5  # Caixa quebra menor (1/5 da altura)

# Função para calcular múltiplas caixas por item
def calculate_multiple_boxes(qtd_pedido, qtd_caixa):
    """Calcula quantas caixas de cada tipo são necessárias para um item"""
    caixas = []
    qtd_restante = qtd_pedido
    
    while qtd_restante > 0:
        if qtd_restante >= qtd_caixa:
            # Caixa cheia
            caixas.append(("caixa_01", 1, qtd_caixa))
            qtd_restante -= qtd_caixa
        else:
            # Caixa quebra - determina o tipo baseado na porcentagem
            porcentagem = qtd_restante / qtd_caixa
            if porcentagem > 0.5:  # > 50% da capacidade
                caixas.append(("caixa_01", 1, qtd_restante))
            elif porcentagem > 0.3:  # Entre 30% e 50%
                caixas.append(("caixa_02", 1/3, qtd_restante))
            else:  # < 30%
                caixas.append(("caixa_03", 1/5, qtd_restante))
            qtd_restante = 0
    
    return caixas

# Função para calcular volumes e pallets com diferentes tipos de caixas
def calculate_volumes_and_pallets(df_pedido, df_base):
    """Calcula volumes e pallets baseado no pedido e na base de dados com diferentes tipos de caixas"""
    
    # Faz o merge dos dados
    df_resultado = df_pedido.merge(df_base, on='item', how='left')
    
    # Identifica itens não encontrados na base
    itens_nao_encontrados = df_resultado[df_resultado['qtd_cx'].isna()]
    
    # Remove itens não encontrados para o cálculo
    df_calculo = df_resultado.dropna(subset=['qtd_cx'])
    
    if len(df_calculo) == 0:
        return None, itens_nao_encontrados
    
    # Lista para armazenar todas as caixas
    todas_caixas = []
    
    # Processa cada item
    for _, row in df_calculo.iterrows():
        item = row['item']
        qtd_pedido = row['qtd']
        qtd_caixa = row['qtd_cx']
        
        # Calcula múltiplas caixas para este item
        caixas_item = calculate_multiple_boxes(qtd_pedido, qtd_caixa)
        
        # Adiciona cada caixa à lista geral
        for i, (tipo_caixa, fator_altura, qtd_na_caixa) in enumerate(caixas_item):
            todas_caixas.append({
                'item': item,
                'qtd_pedido': qtd_pedido,
                'qtd_caixa': qtd_caixa,
                'caixa_num': i + 1,
                'tipo_caixa': tipo_caixa,
                'fator_altura': fator_altura,
                'qtd_na_caixa': qtd_na_caixa,
                'ocupacao_pallet': fator_altura
            })
    
    # Cria DataFrame com todas as caixas
    df_todas_caixas = pd.DataFrame(todas_caixas)
    
    if len(df_todas_caixas) == 0:
        return None, itens_nao_encontrados
    
    # Calcula total de ocupação no pallet
    total_ocupacao = df_todas_caixas['ocupacao_pallet'].sum()
    
    # Calcula pallets necessários
    total_pallets = np.ceil(total_ocupacao / 48)
    
    # Conta tipos de caixas
    contagem_caixas = df_todas_caixas['tipo_caixa'].value_counts()
    
    return {
        'df_detalhado': df_todas_caixas,
        'total_volumes': len(df_todas_caixas),
        'total_pallets': int(total_pallets),
        'total_ocupacao': total_ocupacao,
        'contagem_caixas': contagem_caixas,
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
                
                col1, col2, col3,  = st.columns(3)
                
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
                        help="Baseado na ocupação total no pallet"
                    )

                with col3:
                    st.metric(
                        label="Itens Processados",
                        value=len(resultado['df_detalhado']),
                        help="Itens encontrados na base de dados"
                    )
                
                # Mostra distribuição dos tipos de caixas
                st.subheader("📦 Distribuição dos Tipos de Caixas")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    caixa_01 = resultado['contagem_caixas'].get('caixa_01', 0)
                    st.metric(
                        label="Caixa Padrão (01)",
                        value=caixa_01,
                        help="Caixa padrão - altura completa"
                    )
                
                with col2:
                    caixa_02 = resultado['contagem_caixas'].get('caixa_02', 0)
                    st.metric(
                        label="Caixa Quebra (02)",
                        value=caixa_02,
                        help="1/3 da altura da caixa padrão"
                    )
                
                with col3:
                    caixa_03 = resultado['contagem_caixas'].get('caixa_03', 0)
                    st.metric(
                        label="Caixa Quebra Menor (03)",
                        value=caixa_03,
                        help="1/5 da altura da caixa padrão"
                    )
                
                # Mostra detalhamento
                st.subheader("📋 Detalhamento por Caixa")
                df_detalhado = resultado['df_detalhado'].copy()
                df_detalhado = df_detalhado[['item', 'qtd_pedido', 'qtd_caixa', 'caixa_num', 'qtd_na_caixa', 'tipo_caixa', 'ocupacao_pallet']]
                df_detalhado.columns = ['Item', 'Qtd Pedida', 'Qtd por Caixa', 'Caixa #', 'Qtd na Caixa', 'Tipo de Caixa', 'Ocupação no Pallet']
                df_detalhado['Ocupação no Pallet'] = df_detalhado['Ocupação no Pallet'].round(2)
                
                # Mapeia os tipos de caixa para nomes mais amigáveis
                tipo_caixa_map = {
                    'caixa_01': 'Padrão (01)',
                    'caixa_02': 'Quebra (02)',
                    'caixa_03': 'Quebra Menor (03)'
                }
                df_detalhado['Tipo de Caixa'] = df_detalhado['Tipo de Caixa'].map(tipo_caixa_map)
                
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

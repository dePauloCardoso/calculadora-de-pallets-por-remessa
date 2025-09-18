# 📦 Calculadora de Pallets por Remessa

Esta aplicação Streamlit calcula a quantidade de volumes (caixas) e pallets necessários para um pedido, baseado em uma base de dados de produtos.

## 🚀 Como usar

### 1. Instalação das dependências
```bash
pip install -r requirements.txt
```

### 2. Executar a aplicação
```bash
streamlit run app.py
```

### 3. Usar a aplicação
1. A aplicação abrirá automaticamente no seu navegador
2. Faça upload de um arquivo CSV com as colunas:
   - `item`: código do produto
   - `qtd`: quantidade solicitada
3. A aplicação calculará automaticamente:
   - Quantidade de volumes (caixas) necessários
   - Quantidade de pallets (1 pallet = 48 volumes)

## 📁 Estrutura dos arquivos

- `app.py`: Aplicação principal Streamlit
- `base-dados-produtos.csv`: Base de dados com informações dos produtos (item, qtd_cx)
- `requirements.txt`: Dependências Python necessárias

## 📊 Formato do arquivo de entrada

O arquivo CSV deve conter as seguintes colunas:

| item | qtd |
|------|-----|
| 80101010101 | 100 |
| PG23LA111SD00 | 50 |

## 🔧 Funcionalidades

- ✅ Upload de arquivo CSV
- ✅ Validação de formato
- ✅ Cálculo automático de volumes e pallets
- ✅ Detalhamento por item
- ✅ Identificação de itens não encontrados na base
- ✅ Download dos resultados
- ✅ Interface responsiva e intuitiva

## 📈 Cálculos realizados

1. **Volumes por item**: `ceil(quantidade_pedida / qtd_por_caixa)`
2. **Total de volumes**: Soma de todos os volumes por item
3. **Total de pallets**: `ceil(total_volumes / 48)`

## ⚠️ Observações

- Itens com `qtd_cx = 0` na base de dados são ignorados
- Itens não encontrados na base são listados separadamente
- A aplicação usa cache para melhor performance
# calculadora-de-pallets-por-remessa

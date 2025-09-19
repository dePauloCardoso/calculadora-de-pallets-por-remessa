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

### Sistema de Caixas
A aplicação utiliza 3 tipos de caixas baseados na quantidade do pedido:

- **Caixa Padrão (01)**: Altura completa - usada quando quantidade > 50% da capacidade
- **Caixa Quebra (02)**: 1/3 da altura - usada quando quantidade está entre 30% e 50% da capacidade  
- **Caixa Quebra Menor (03)**: 1/5 da altura - usada quando quantidade < 30% da capacidade

### Cálculos
1. **Caixas cheias**: Quando quantidade ≥ capacidade da caixa
2. **Caixa quebra**: Para o restante, baseado na porcentagem:
   - > 50% da capacidade: Caixa Padrão (01)
   - 30% - 50% da capacidade: Caixa Quebra (02)
   - < 30% da capacidade: Caixa Quebra Menor (03)
3. **Ocupação no pallet**: Cada tipo de caixa tem um fator de ocupação diferente
4. **Total de pallets**: `ceil(ocupação_total / 48)`

### Exemplo
Pedido de 22 itens, caixa comporta 12:
- 1ª caixa: 12 itens (cheia) = Caixa Padrão (01)
- 2ª caixa: 10 itens (83%) = Caixa Padrão (01)

### Equivalências
- 1 pallet = 48 caixas padrão
- 1 caixa padrão = 3 caixas quebra = 5 caixas quebra menor

## ⚠️ Observações

- Itens com `qtd_cx = 0` na base de dados são ignorados
- Itens não encontrados na base são listados separadamente
- A aplicação usa cache para melhor performance
# calculadora-de-pallets-por-remessa

# API Dados Econômicos (AWS Lambda + Glue + Athena)

Este projeto coleta, transforma e armazena indicadores econômicos provenientes de APIs públicas do Brasil e exterior.
A ingestão ocorre diariamente via **AWS Lambda**, os dados são salvos em formato **Parquet particionado** no **Amazon S3**, e posteriormente disponibilizados para consulta SQL através do **AWS Glue Data Catalog** e **Amazon Athena**.

O objetivo é criar uma pipeline simples, confiável e barata para centralização de indicadores como:

- SELIC diária
- Boletim Focus (Expectativas de Mercado — anual/mensal)
- Dólar PTAX diário
- IPCA (IBGE)
- Taxas do Tesouro Direto

---

## 🔥 Principais funcionalidades

- Coleta automática de indicadores econômicos via AWS Lambda
- Transformação padronizada dos dados (schema consistente + metadados)
- Salvamento otimizado no S3 em **Parquet particionado por `dt_execucao`**
- Criação de catálogo no **AWS Glue** para consulta via Athena
- Execução diária automática via **EventBridge Scheduler**
- Testes funcionais para validar construção das URLs e formatação de datas
- Suporte a execução local para desenvolvimento e debug

---

## ✔ Tecnologias utilizadas

- **AWS Lambda** (Python runtime)
- **AWS EventBridge** (scheduler diário)
- **Amazon S3** (data lake)
- **AWS Glue Crawler + Glue Data Catalog**
- **Amazon Athena**
- Python 3.10+
- `requests`, `boto3`, `pandas`, `pyarrow`
- `pytest`

---

## 📋 Sumário

- [Descrição](#-descrição)
- [Arquitetura](#-arquitetura)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Variáveis de ambiente](#-variáveis-de-ambiente)
- [Execução local](#-execução-local)
- [Execução em Produção](#-execução-em-produção-lambda--eventbridge)
- [Integração com Glue e Athena](#-integração-com-glue-e-athena)
- [Estrutura do projeto](#-estrutura-do-projeto)
- [Testes](#-testes)
- [Contribuição](#-contribuição)

---

## 📌 Descrição

A função principal `lambda_handler(event, context)` é capaz de:

- Executar **uma API específica** (filtro por `api_name`)
- Executar **todas as APIs simultaneamente** (usando `run_all: true`)
- Ajustar automaticamente para o **dia útil** mais próximo (ignorando finais de semana e feriados)
- Transformar e padronizar os dados em um schema consistente
- Salvar em:
  - **S3** em formato JSON (ambiente local) ou **Parquet particionado** (em produção com Glue)
  - **AWS Glue Data Catalog** (metadados automáticos)

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                     EventBridge Scheduler                       │
│                    (diariamente às 10:00 UTC)                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AWS Lambda                                 │
│                   (main.lambda_handler)                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 1. Calcula data útil (ignorando fins de semana/feriados)  │ │
│  │ 2. Busca indicadores das APIs públicas                    │ │
│  │ 3. Transforma em schema padronizado                       │ │
│  │ 4. Escreve no S3                                          │ │
│  └────────────────────────────────────────────────────────────┘ │
└──┬──────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────────┐
│            Amazon S3 (Data Lake)                                │
│  s3://bucket/dados/economicos/                                 │
│  ├── selic/dt_execucao=YYYY-MM-DD/data.parquet               │
│  ├── focus/dt_execucao=YYYY-MM-DD/data.parquet               │
│  ├── dolar/dt_execucao=YYYY-MM-DD/data.parquet               │
│  ├── ibge/dt_execucao=YYYY-MM-DD/data.parquet                │
│  └── tesouro/dt_execucao=YYYY-MM-DD/data.parquet             │
└──┬──────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────────┐
│            AWS Glue Crawler (automático)                        │
│  Atualiza schema das tabelas a cada novo particionamento       │
└──┬──────────────────────────────────────────────────────────────┘
   │
   ▼
┌─────────────────────────────────────────────────────────────────┐
│         AWS Glue Data Catalog + Amazon Athena                  │
│  Consultas SQL ad-hoc em dados econômicos históricos            │
│                                                                 │
│  Exemplo:                                                       │
│  SELECT * FROM dados_economicos.selic                           │
│  WHERE dt_execucao >= '2025-11-01'                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ Pré-requisitos

### Localmente

- **Python 3.10+**
- Variáveis de ambiente (arquivo `.env`)

### Em Produção (AWS)

- **AWS Lambda** com role IAM que conceda:
  - `s3:GetObject`, `s3:PutObject` no bucket alvo
  - `glue:PutDataCatalogEncryptionSettings`, `glue:BatchCreatePartition` (optional, se usar Crawler)
- **AWS EventBridge** (scheduler)
- **AWS Glue Crawler** (optional, para atualização automática do catálogo)
- **Amazon Athena** (para consultas SQL)

---

## 📦 Instalação

### 1. Clonar repositório

```bash
git clone https://github.com/GabrielMendes-data/project-dados-economicos-lambda.git
cd project-dados-economicos-lambda
```

### 2. Criar ambiente virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependências

```powershell
pip install -r requirements.txt
```

---

## 🔐 Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com as variáveis abaixo:

```env
# ========== URLs das APIs ==========
BCB_SELIC_URL=https://api.bcb.gov.br/dados/serie/bcdata.sgs.1178/dados
BCB_FOCUS_URL=https://olinda.bcb.gov.br/olinda/servico/ExpectativasMercado/versao/v1/odata
BCB_DOLAR_URL=https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarDia(dataCotacao=@dataCotacao)
IBGE_IPCA_URL=https://apisidra.ibge.gov.br/values
TESOURO_TAXAS_URL=https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download
FERIADOS_URL=https://date.nager.at/api/v3/PublicHolidays

# ========== Configuração de Execução ==========
BUCKET=seu-bucket-s3
ALL_APIS=selic,focus,dolar,ibge,tesouro
FOCUS_INDICATORS=Selic,IPCA,Câmbio
FOCUS_TEMPORAL_SERIES=anual,mensal

# ========== AWS (se usar em Produção) ==========
AWS_REGION=sua-regiao
AWS_ACCESS_KEY_ID=seu-access-key
AWS_SECRET_ACCESS_KEY=sua-secret-key

# ========== Logging ==========
LOG_LEVEL=INFO
```

> **Nota:** Credenciais AWS podem também ser configuradas via:
> - Variáveis de ambiente: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
> - Arquivo `~/.aws/credentials`
> - Perfil IAM (se executar em EC2 ou Lambda)

---

## 🚀 Execução local

### Executar o handler manualmente

```powershell
python main.py
```

O arquivo `main.py` possui um bloco `if __name__ == '__main__'` que executa exemplos.

### Exemplos de eventos

Invocar via Python REPL:

```python
from main import lambda_handler

# Executar uma API específica
resultado = lambda_handler({
    "api_name": "selic",
    "date": "2025-11-14"
})
print(resultado)

# Executar todas as APIs
resultado = lambda_handler({
    "run_all": True,
    "date": "2025-11-14"
})
print(resultado)
```

---

## ⚡ Execução em Produção (Lambda + EventBridge)

### 1. Preparar pacote ZIP ou container docker

```powershell
# Criar diretório temporário
mkdir lambda-package
cd lambda-package

# Copiar código-fonte
cp -r ..\src .
cp -r ..\main.py .
cp -r ..\requirements.txt .

# Instalar dependências
pip install -r requirements.txt -t .

# Criar ZIP
Compress-Archive -Path * -DestinationPath function.zip

# Fazer upload para Lambda
# (via console AWS ou via CLI)
```

### 2. Configurar a função Lambda

No **AWS Lambda Console**:

1. Criar função: `nome-lambda`
2. Runtime: `Python 3.11` ou superior
3. Handler: `main.lambda_handler`
4. Timeout: `30 segundos` (mínimo recomendado)
5. Memory: `512 MB` (mínimo recomendado)
6. Adicionar as variáveis de ambiente (`.env`)
7. Anexar role IAM com permissões de S3 e Glue

### 3. Agendar com EventBridge Scheduler

No **AWS EventBridge Console**:

1. Criar agendamento: `dados-economicos-diario`
2. Frequência: `cron(0 9 * * ? *)` (9:00 UTC, segunda a domingo)
3. Alvo: Função Lambda `dados-economicos-lambda`
4. Payload de entrada (JSON):
   ```json
   {
     "run_all": true
   }
   ```

---

## 🔗 Integração com Glue e Athena

### AWS Glue Crawler

Para criar tabelas automaticamente no **Glue Data Catalog**:

1. No **AWS Glue Console**, criar Crawler:
   - Nome: `nome-crawler`
   - Fonte: S3 bucket `bucket-s3`
   - Banco de dados: `database` (criar se não existir)

2. Executar crawler após cada ingestão de dados (ou agendar).

---

## 📁 Estrutura do projeto

```text
.
├── conftest.py                      # Configurações pytest
├── Dockerfile                       # Container para Lambda
├── main.py                          # Handler principal (lambda_handler)
├── README.md                        # Este arquivo
├── requirements.txt                 # Dependências Python
├── src/
│   ├── domain/
│   │   ├── date.py                 # Utilitários de data e feriados
│   │   ├── logger.py               # Configuração de logging centralizada
│   │   └── transform_data.py       # Transformações e factory de APIs
│   │
│   └── infra/
│       └── fetch_data.py           # Clientes HTTP (interfaces por API)

└── tests/
    └── test_fetch_data.py          # Testes funcionais das APIs
```

### Descrição dos módulos

- **`main.py`**: Ponto de entrada. Contém `lambda_handler()` e lógica orquestradora.
- **`src/domain/date.py`**: Cálculo de datas úteis, busca de feriados via API.
- **`src/domain/logger.py`**: Configuração centralizada de logging (nível via `LOG_LEVEL`).
- **`src/domain/transform_data.py`**: Classes de transformação por API + factory pattern.
- **`src/infra/fetch_data.py`**: Classes abstratas e implementações de clientes HTTP.
- **`tests/test_fetch_data.py`**: Testes funcionais (validam URLs e requisições reais).

---

## 🧪 Testes

### Executar todos os testes

```powershell
pytest -v
```

### Executar testes específicos

```powershell
# Apenas testes de Selic
pytest tests/test_fetch_data.py::test_selic_build_url_and_fetch_data -v

# Com cobertura
pytest --cov=src --cov-report=html
```
---

## 🤝 Contribuição

1. **Fork** este repositório.
2. Crie uma **branch** com nome descritivo:
   ```bash
   git checkout -b feature/nova-api-economica
   ```
3. Faça as mudanças e **adicione testes** (se aplicável).
4. Garanta que os testes passam:
   ```powershell
   pytest -q
   ```
5. Abra um **Pull Request** com descrição clara.

**Última atualização:** Novembro 2025

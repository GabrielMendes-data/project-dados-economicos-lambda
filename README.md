# API Dados Econômicos (Lambda)

Projeto que coleta, transforma e salva dados econômicos de várias APIs públicas
usando uma função AWS Lambda ou execução local. O objetivo é centralizar indicadores
como SELIC, IPCA, câmbio, expectativas do mercado e taxas do Tesouro Direto.

**Principais funcionalidades:**
- Coleta de dados de múltiplas APIs (BCB, IBGE, Tesouro Direto).
- Salvamento em S3 via `boto3` quando executado em AWS.
- Testes funcionais para validação de construção de URLs.

**Tecnologias:** Python 3.10+, `requests`, `boto3`, `pytest`.

**Sumário**
- **Descrição**
- **Pré-requisitos**
- **Instalação**
- **Variáveis de ambiente**
- **Execução local**
- **Deployment (Lambda)**
- **Testes**
- **Desenvolvimento**
- **Contribuição**

**Estrutura do projeto**

Exemplo da árvore de diretórios e arquivos mais importantes do projeto:

```text
.
├── conftest.py
├── Dockerfile
├── main.py
├── README.md
├── requirements.txt
├── src/
│   ├── domain/
│   │   ├── date.py
│   │   ├── transform_data.py
│   │   └── logger.py
│   └── infra/
│       └── fetch_data.py
└── tests/
	└── test_fetch_data.py
```

Breve descrição dos diretórios:
- `src/domain`: regras de negócio e transformações dos dados.
- `src/infra`: clientes HTTP e integrações com APIs externas.
- `tests`: testes automatizados (pytest).


**Descrição**

O projeto expõe uma função `lambda_handler(event, context)` em `main.py` que pode
ser acionada via EventBridge (ou manualmente) para coletar os dados de uma ou
de todas as APIs configuradas. Os dados são transformados e carregados em um
bucket S3 configurado.

**Pré-requisitos**
- Python 3.10 ou superior
- AWS credentials configuradas localmente em arquivo .env (se for gravar no S3)
- Variáveis de ambiente listadas abaixo

**Configuração**
Instale dependências em um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Variáveis de ambiente**

Crie um arquivo `.env` na raiz com as variáveis abaixo (exemplo):

```env
# URLs das APIs
BCB_SELIC_URL=<url_base_selic>
BCB_FOCUS_URL=<url_base_focus>
BCB_DOLAR_URL=<url_base_dolar>
IBGE_IPCA_URL=<url_base_ibge>
TESOURO_TAXAS_URL=<url_base_tesouro>
FERIADOS_URL=https://date.nager.at/api/v3/PublicHolidays

# Configuração de execução
BUCKET=<nome-do-bucket-s3>
ALL_APIS=selic,focus,dolar,ibge,tesouro
FOCUS_INDICATORS=Selic,IPCA,Câmbio
FOCUS_TEMPORAL_SERIES=anual/mensal

# Logging (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

- **AWS**: Para gravar no S3, garanta que as credenciais da AWS estejam
	configuradas (por exemplo via `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` ou
	perfil do AWS CLI).

**Execução local**

Executar `main.py` para testes locais. O arquivo já possui um bloco `if __name__ == '__main__'`
que executa chamadas de exemplo.

```powershell
python main.py
```


Exemplos de eventos suportados pela função:

- Executar todas as APIs:

```json
{ "run_all": true, "date": "2025-11-14" }
```

- Executar apenas uma API:

```json
{ "api_name": "dolar", "date": "2025-11-14" }
```

**Deployment (AWS Lambda)**

1. Empacote as dependências em um ZIP ou conteiner docker.
2. Configure variáveis de ambiente na função Lambda conforme `.env`.
3. Conceda permissão ao Lambda para gravar no S3 (`s3:PutObject`) no bucket alvo.

**Testes**

Os testes funcionais estão em `tests/test_fetch_data.py`. Eles validam a construção
das URLs e fazem requisições HTTP reais. Para executar:

```powershell
pip install -r requirements.txt
pytest -q
```

Comandos úteis:

```powershell
# Formatar
black .

# Rodar testes
pytest -q

# Executar script local
python main.py
```

**Contribuição**

1. Fork e branch com nome descritivo (ex.: `feature/minha-nova-funcionalidade`).
2. Abra um Pull Request com descrição clara e referência a issues.
3. Garanta que os testes existentes passem e adicione novos testes quando
	pertinente.

import os
import json
import boto3
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

from src.domain.transform_data import FactoryAPIs
from src.domain.date import DateUtil

# ============================
# Carregar variáveis de ambiente
# ============================
load_dotenv()

BUCKET = os.environ["BUCKET"]
ALL_APIS = os.environ["ALL_APIS"].split(",")
FOCUS_INDICATORS = os.environ["FOCUS_INDICATORS"].split(",")
FOCUS_TEMPORAL_SERIES = os.environ["FOCUS_TEMPORAL_SERIES"]

s3 = boto3.client("s3")


import awswrangler as wr

def salvar_parquet_s3(bucket, key, data):
    df = pd.DataFrame(data)

    s3_path = f"s3://{bucket}/{key}"

    df.to_parquet(
        s3_path,
        index=False,
        compression="snappy"
    )


def lambda_handler(event, context=None):
    """
    EventBridge envia algo assim:

    {
        "run_all": true,
        "date": "2025-11-14"
    }

    Ou execução manual:
    {
        "api_name": "dolar",
        "date": "2025-11-14"
    }
    """

    # 1. DATA DO EVENTO
    event_date = event.get("date")

    if event_date:
        # formato vindo do EventBridge (YYYY-MM-DD)
        dt = datetime.strptime(event_date, "%Y-%m-%d")
    else:
        dt = datetime.now()

    # 2. CONVERTER PARA DIA ÚTIL
    data_util = DateUtil(dt).date_util()  # retorna "dd/mm/YYYY"

    # 3. DEFINIR QUAIS APIS EXECUTAR
    run_all = event.get("run_all", False)

    if run_all:
        apis_to_run = ALL_APIS
    else:
        apis_to_run = [event.get("api_name", "selic")]

    resultados = []

    # 4. EXECUTAR CADA API
    for api_name in apis_to_run:

        # parâmetros mínimos
        params = {"date": data_util}

        # API Focus exige parâmetros adicionais
        if api_name == "focus":
            params.update(
                {
                    "indicator": FOCUS_INDICATORS,
                    "temporal_series": FOCUS_TEMPORAL_SERIES,
                }
            )

        # Chamar a factory e fazer o ETL da API
        data = FactoryAPIs.execute_api(api_name, params)

        # 5. SALVAR NO S3
        if data:
            dt_folder = datetime.strptime(data_util, "%d/%m/%Y").strftime("%Y-%m-%d")

            key = (
                f"{api_name}/"
                f"dt_execucao={dt_folder}/"
                f"{api_name}-{dt_folder}.parquet"
            )

            salvar_parquet_s3(BUCKET, key, data)

            resultados.append(
                {"api": api_name, "registros": len(data), "params_usados": params}
            )
        else:
            resultados.append(
                {
                    "api": api_name,
                    "registros": 0,
                    "params_usados": params,
                    "erro": "API não retornou dados",
                }
            )

    # 6. RETORNO FINAL
    return {
        "status": "ok",
        "data_util_processada": data_util,
        "apis_executadas": resultados,
    }


# ============================
# TESTE LOCAL
# ============================
if __name__ == "__main__":
    # testar rodando unica api
    resposta_single_api = lambda_handler(
        event={"api_name": "ibge", "date": datetime.now().strftime("%Y-%m-%d")}
    )

    print(json.dumps(resposta_single_api, indent=4, ensure_ascii=False))

    # testar rodando todas api's
    resposta_all_api = lambda_handler(
        event={"run_all": True, "date": datetime.now().strftime("%Y-%m-%d")}
    )

    print(json.dumps(resposta_all_api, indent=4, ensure_ascii=False))
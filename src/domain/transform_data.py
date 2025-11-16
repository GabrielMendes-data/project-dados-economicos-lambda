from datetime import datetime
from src.domain.logger import get_logger
logger = get_logger("transform")

from src.infra.fetch_data import (
    SelicFetchData,
    FocusFetchData,
    DolarFetchData,
    IbgeFetchData,
    TesouroFetchData,
)


class ColDtReferencia:

    @staticmethod
    def add_dt_referencia(data: list[dict], date: str) -> list[dict]:
        for item in data:
            item["dt_execucao"] = datetime.strptime(date, "%d/%m/%Y").strftime(
                "%Y-%m-%d"
            )
        return data


class TransformFocusData:
    def __init__(self, indicators: list[str], date: str, temporal_series: str):
        logger.info(f"[Focus] Iniciando transform - indicators={indicators}, date={date}, serie={temporal_series}")

        if not isinstance(indicators, list):
            logger.error(f"[Focus] Indicator deve ser lista. Recebido: {indicators}")
            raise TypeError("Indicator deve ser uma lista de strings.")

        self.indicators = indicators

        dt_date = datetime.strptime(date, "%d/%m/%Y").date()
        self.date = [date, dt_date.replace(year=dt_date.year + 1).strftime("%d/%m/%Y")]
        self.temporal_series = temporal_series

    def transform(self) -> list[dict]:
        result_focus = []

        for indicator in self.indicators:
            for date in self.date:
                logger.info(f"[Focus] Consumindo API - indicador={indicator} date={date}")

                fetch_data = FocusFetchData().fetch_data(indicator, date, self.temporal_series)

                if not fetch_data:
                    logger.warning(f"[Focus] API não retornou dados - indicador={indicator}, date={date}")
                    continue

                try:
                    dict_filtered = fetch_data[-1]
                except Exception as e:
                    logger.error(f"[Focus] Erro ao acessar último item: {e}")
                    continue

                keys = ["Indicador", "Data", "DataReferencia", "Mediana"]
                dict_filtered = {key: dict_filtered.get(key) for key in keys}

                result_focus.append(dict_filtered)

        result_focus = ColDtReferencia.add_dt_referencia(result_focus, self.date[0])

        logger.info(f"[Focus] Transform finalizado. Registros={len(result_focus)}")
        return result_focus


class TransformIbgeData:
    def __init__(self, date: str):
        logger.info(f"[IBGE] Iniciando transform - date={date}")
        self.date = date

    def transform(self) -> list[dict]:
        fetch_data = IbgeFetchData().fetch_data(self.date)

        if not isinstance(fetch_data, list):
            logger.error(f"[IBGE] Erro: fetch_data precisa ser lista. Valor retornado: {fetch_data}")
            raise TypeError("fetch_data precisa ser uma lista!")

        logger.info(f"[IBGE] Registros recebidos: {len(fetch_data)}")

        # Arrays de mapeamento para substituir os nomes das keys
        keys = ["V", "D2C", "D3C", "D3N"]
        new_keys = ["valor_ipca", "ano_mes", "variavel_codigo", "variavel_nome"]

        # Converter nomes das keys
        if isinstance(fetch_data, list):
            # Itera pela lista e transforma cada item (dicionário)
            data_transform = [
                {new_keys[keys.index(k)]: v for k, v in item.items() if k in keys}
                for item in fetch_data
            ]
        else:
            raise TypeError("fetch_data precisa ser uma lista!")

        variaveis = ["63", "2265"]
        result_ibge = [
            {key: item[key] for key in new_keys}
            for item in data_transform[1:]
            if item.get("variavel_codigo") in variaveis
        ]

        result_ibge = ColDtReferencia.add_dt_referencia(result_ibge, self.date)

        return result_ibge


class TransformSelicData:
    def __init__(self, date: str):
        logger.info(f"[Selic] Transform iniciado - date={date}")
        self.date = date

    def transform(self) -> list[dict]:
        fetch_data = SelicFetchData().fetch_data(self.date)

        if not fetch_data:
            logger.warning(f"[Selic] API retornou vazio para date={self.date}")

        result_selic = ColDtReferencia.add_dt_referencia(fetch_data, self.date)
        logger.info(f"[Selic] Transform finalizado. Registros={len(fetch_data)}")
        return result_selic


class TransformDolarData:
    def __init__(self, date: str):
        logger.info(f"[Dolar] Transform iniciado - date={date}")
        self.date = date

    def transform(self) -> list[dict]:
        fetch_data = DolarFetchData().fetch_data(self.date)

        if not fetch_data:
            logger.warning(f"[Dolar] API retornou vazio para date={self.date}")

        result = ColDtReferencia.add_dt_referencia(fetch_data, self.date)
        logger.info(f"[Dolar] Transform finalizado. Registros={len(result)}")
        return result


class TransformTesouroData:
    def __init__(self, date: str):
        logger.info(f"[Tesouro] Transform iniciado - date={date}")
        self.date = date

    def transform(self) -> list[dict]:
        fetch_data = TesouroFetchData().fetch_data(self.date)

        if not fetch_data:
            logger.warning(f"[Tesouro] API retornou vazio para date={self.date}")

        result = ColDtReferencia.add_dt_referencia(fetch_data, self.date)
        logger.info(f"[Tesouro] Transform finalizado. Registros={len(result)}")
        return result


class FactoryAPIs:
    @staticmethod
    def execute_api(api_name: str, params: dict) -> list[dict]:
        try:
            if api_name == "selic":
                return TransformSelicData(params["date"]).transform()
            elif api_name == "focus":
                return TransformFocusData(
                    params["indicator"], params["date"], params["temporal_series"]
                ).transform()
            elif api_name == "dolar":
                return TransformDolarData(params["date"]).transform()
            elif api_name == "ibge":
                return TransformIbgeData(params["date"]).transform()
            elif api_name == "tesouro":
                return TransformTesouroData(params["date"]).transform()
            else:
                raise ValueError(f"API {api_name} não encontrada")

        except Exception as e:
            logger.error(f"[Factory] Erro ao executar API '{api_name}': {e}", exc_info=True)
            raise
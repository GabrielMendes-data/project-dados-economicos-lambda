import random
import requests
from datetime import datetime, timedelta

from src.domain.date import DateUtil

from src.infra.fetch_data import (
    SelicFetchData,
    FocusFetchData,
    DolarFetchData,
    IbgeFetchData,
    TesouroFetchData,
)


def gerar_data_aleatoria():

    # Início do ano atual
    inicio_do_ano = datetime(datetime.now().year, 1, 1)

    # Quantos dias se passaram desde o início do ano até hoje
    dias_passados = (datetime.now() - inicio_do_ano).days

    # Sorteia um dia dentro desse intervalo
    dias_aleatorios = random.randint(0, dias_passados)

    # Constrói a data aleatória
    data = inicio_do_ano + timedelta(days=dias_aleatorios)

    # Ajusta para data útil usando sua lógica central

    return DateUtil(data).date_util()


def gerar_indicador_aleatorio():
    return random.choice(["Selic", "IPCA", "Câmbio"])


def gerar_serie_temporal_aleatoria():
    return random.choice(["anual", "mensal"])


# ========== Testes Funcionais ==========


def test_selic_build_url_and_fetch_data():
    selic = SelicFetchData()
    data = gerar_data_aleatoria()
    print(f"Data: {data}")
    url = selic.build_url(data)
    print(f"URL: {url}")

    r = requests.get(url, timeout=30)
    assert r.status_code == 200


def test_focus_build_url_and_fetch_data():
    focus = FocusFetchData()
    data = gerar_data_aleatoria()
    print(f"Data: {data}")
    url = focus.build_url(
        gerar_indicador_aleatorio(), data, gerar_serie_temporal_aleatoria()
    )
    print(f"URL: {url}")

    r = requests.get(url, timeout=30)
    assert r.status_code == 200


def test_dolar_build_url_and_fetch_data():
    dolar = DolarFetchData()
    data = gerar_data_aleatoria()
    print(f"Data: {data}")
    url = dolar.build_url(data)
    print(f"URL: {url}")

    r = requests.get(url, timeout=30)
    assert r.status_code == 200


def test_ibge_build_url_and_fetch_data():
    ibge = IbgeFetchData()
    data = gerar_data_aleatoria()
    print(f"Data: {data}")
    url = ibge.build_url(data)
    print(f"URL: {url}")

    r = requests.get(url, timeout=30)
    assert r.status_code == 200


def test_tesouro_build_url_and_fetch_data():
    tesouro = TesouroFetchData()
    data = gerar_data_aleatoria()
    print(f"Data: {data}")
    url = tesouro.build_url(data)
    print(f"URL: {url}")

    r = requests.get(url, timeout=30)
    assert r.status_code == 200

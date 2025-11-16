from datetime import datetime, timedelta
import yaml
import pandas as pd
import requests
from typing import List, Dict
from dotenv import load_dotenv
import os


class DateUtil:

    load_dotenv()
    FERIADOS_URL = os.getenv("FERIADOS_URL")

    def __init__(self, date: datetime):
        """
        date: objeto datetime
        """
        self.date = date

    def build_url(self):
        """
        Construir URL para capturar feriados via API
        """
        return f"{self.FERIADOS_URL}/{self.date.year}/BR"

    def fetch_data(self) -> List[Dict]:
        """
        Busca feriados via API pública
        """
        url = self.build_url()
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()

    def feriados(self):
        """
        Retorna dict {Timestamp: nome_do_feriado}
        Apenas feriados nacionais (global = True)
        """
        data = self.fetch_data()

        feriados = {
            pd.Timestamp(h["date"]): h["localName"]
            for h in data
            if (
                (("Public" in h.get("types", [])) or ("Bank" in h.get("types", [])))
                and h.get("global", False)
            )
        }

        return feriados

    def date_util(self, dias: int = 1):
        """
        Retorna a data útil D - (dias)
        Ignora finais de semana e feriados
        """
        date = self.date
        feriados = self.feriados()
        count = 0

        while count < dias:
            date -= timedelta(days=1)

            if date.weekday() >= 5:  # sábado (5), domingo (6)
                continue

            if pd.Timestamp(date) in feriados:
                continue

            count += 1

        return date.strftime("%d/%m/%Y")
import json
import os
from datetime import datetime, timedelta, timezone

import requests
import streamlit as st

FUSO_BRASILIA = timezone(timedelta(hours=-3))


def _url_base():
    """Endereço do Firebase, guardado em Secrets. Sem ele, usa arquivo local."""
    try:
        return st.secrets["FIREBASE_URL"].rstrip("/")
    except Exception:
        return None


def carregar_estado(site):
    """Devolve o progresso do site, {} se estiver vazio ou None se der erro."""
    base = _url_base()
    if base:
        try:
            resp = requests.get(f"{base}/checklists/{site}.json", timeout=5)
            resp.raise_for_status()
            return resp.json() or {}
        except Exception:
            return None
    arquivo = f"estado_{site}.json"
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def salvar_estado(site, estado):
    """Grava o progresso junto com o horário da última alteração."""
    dados = dict(estado)
    dados["atualizado_em"] = datetime.now(FUSO_BRASILIA).strftime("%d/%m/%Y %H:%M:%S")
    base = _url_base()
    if base:
        try:
            resp = requests.put(f"{base}/checklists/{site}.json", json=dados, timeout=5)
            resp.raise_for_status()
        except Exception:
            st.error("Não consegui salvar o progresso. Confira a internet e tente de novo.")
        return
    with open(f"estado_{site}.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def registrar_finalizacao(site, operador, feitos, total):
    """Guarda no histórico quem finalizou o checklist e quando."""
    registro = {
        "data": datetime.now(FUSO_BRASILIA).strftime("%d/%m/%Y %H:%M:%S"),
        "operador": operador,
        "feitos": feitos,
        "total": total,
    }
    base = _url_base()
    if base:
        try:
            resp = requests.post(f"{base}/historico/{site}.json", json=registro, timeout=5)
            resp.raise_for_status()
        except Exception:
            st.error("Não consegui salvar a finalização. Tente de novo.")
        return registro
    arquivo = f"historico_{site}.json"
    lista = []
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            lista = json.load(f)
    lista.append(registro)
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)
    return registro


def carregar_historico(site, limite=5):
    """Devolve as últimas finalizações, da mais recente pra mais antiga."""
    base = _url_base()
    if base:
        try:
            resp = requests.get(
                f"{base}/historico/{site}.json",
                params={"orderBy": '"$key"', "limitToLast": limite},
                timeout=5,
            )
            resp.raise_for_status()
            dados = resp.json() or {}
            return [dados[chave] for chave in sorted(dados, reverse=True)]
        except Exception:
            return []
    arquivo = f"historico_{site}.json"
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            return list(reversed(json.load(f)))[:limite]
    return []

import streamlit as st

from banco import carregar_estado, registrar_finalizacao, salvar_estado
from roteiros import ROTEIROS

SITE = "arena"
R = ROTEIROS[SITE]

st.set_page_config(page_title=f"Checklist {R['nome']}", page_icon="✅")

if "estado" not in st.session_state:
    st.session_state.estado = carregar_estado(SITE) or {}

total_itens = sum(len(lista) for lista in R["secoes"].values())

st.title(f"Checklist {R['nome']}")
st.caption("Marque cada item conforme for concluindo. O progresso fica salvo.")

if R["topo"]:
    st.warning(R["topo"])

nome_voluntario = st.text_input(
    "Nome do voluntário na operação",
    value=st.session_state.estado.get("voluntario", ""),
    key="voluntario_input",
)
if nome_voluntario != st.session_state.estado.get("voluntario", ""):
    st.session_state.estado["voluntario"] = nome_voluntario
    salvar_estado(SITE, st.session_state.estado)

area_progresso = st.container()

st.divider()

for secao, lista_itens in R["secoes"].items():
    st.subheader(secao)
    for indice, texto in enumerate(lista_itens):
        chave = f"item-{secao}-{indice}"
        marcado = st.session_state.estado.get(chave, False)
        novo_valor = st.checkbox(texto, value=marcado, key=chave)
        if novo_valor != marcado:
            st.session_state.estado[chave] = novo_valor
            salvar_estado(SITE, st.session_state.estado)

    if secao == "Antes do culto":
        for aviso in R["avisos_antes"]:
            st.info(aviso)
        st.divider()

    if secao == "Depois do culto" and R["aviso_depois"]:
        st.warning(R["aviso_depois"])

total_feitos = sum(
    1 for chave, valor in st.session_state.estado.items()
    if chave.startswith("item-") and valor
)
with area_progresso:
    st.progress(total_feitos / total_itens if total_itens else 0)
    st.write(f"{total_feitos} de {total_itens} concluídos")

st.divider()

st.subheader("Finalizar")
if st.session_state.estado.get("finalizado_em"):
    st.success(
        f"Finalizado por {st.session_state.estado.get('finalizado_por', '')} "
        f"em {st.session_state.estado['finalizado_em']}."
    )
else:
    if total_feitos < total_itens:
        st.warning(f"Ainda faltam {total_itens - total_feitos} itens sem marcar.")
    if st.button("Finalizar e salvar", type="primary"):
        operador = st.session_state.estado.get("voluntario", "").strip()
        if not operador:
            st.error("Preencha o nome do voluntário no topo antes de finalizar.")
        else:
            registro = registrar_finalizacao(SITE, operador, total_feitos, total_itens)
            st.session_state.estado["finalizado_por"] = operador
            st.session_state.estado["finalizado_em"] = registro["data"]
            salvar_estado(SITE, st.session_state.estado)
            st.rerun()

st.divider()

if st.button("Reiniciar checklist", type="secondary"):
    st.session_state.estado = {}
    # Os checkboxes guardam o próprio valor em st.session_state com a mesma
    # chave. Sem apagar isso, continuam marcados na tela após o reset.
    for chave in list(st.session_state.keys()):
        if chave.startswith("item-") or chave == "voluntario_input":
            del st.session_state[chave]
    salvar_estado(SITE, st.session_state.estado)
    st.rerun()

st.caption(
    "Tudo que vem da gestão são ordens pastorais. Primeiro execute o que foi "
    "pedido; sugestões só depois, direto com a gestão."
)

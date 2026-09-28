import streamlit as st

from banco import carregar_estado, modo_local, registrar_finalizacao, salvar_estado
from estilo import ICONES, abrir_cartao, aplicar_estilo, fechar_cartao
from roteiros import ROTEIROS

SITE = "iluminacao"
R = ROTEIROS[SITE]
ICONE = ICONES.get(SITE, "✅")

st.set_page_config(page_title=f"Checklist {R['nome']}", page_icon=ICONE)
aplicar_estilo(
    f"Checklist {R['nome']}",
    ICONE,
    "Marque cada item conforme for concluindo. O progresso fica salvo.",
)

if modo_local():
    st.warning(
        "Banco de dados não configurado (falta FIREBASE_URL em Secrets). "
        "O progresso está sendo salvo só neste site e o painel não vai enxergar."
    )

if "estado" not in st.session_state:
    st.session_state.estado = carregar_estado(SITE) or {}

if R["topo"]:
    st.warning(R["topo"])

total_itens = sum(len(lista) for lista in R["secoes"].values())

abrir_cartao()
st.markdown("#### 👤 Voluntário na operação")
nome_voluntario = st.text_input(
    "Nome do voluntário",
    value=st.session_state.estado.get("voluntario", ""),
    key="voluntario_input",
    label_visibility="collapsed",
    placeholder="Digite o nome de quem está operando",
)
if nome_voluntario != st.session_state.estado.get("voluntario", ""):
    st.session_state.estado["voluntario"] = nome_voluntario
    salvar_estado(SITE, st.session_state.estado)
fechar_cartao()

area_progresso = st.container()

for secao, lista_itens in R["secoes"].items():
    abrir_cartao()
    st.markdown(f"#### {secao}")
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

    if secao == "Depois do culto" and R["aviso_depois"]:
        st.warning(R["aviso_depois"])
    fechar_cartao()

total_feitos = sum(
    1 for chave, valor in st.session_state.estado.items()
    if chave.startswith("item-") and valor
)
with area_progresso:
    abrir_cartao()
    st.markdown("#### Progresso")
    st.progress(total_feitos / total_itens if total_itens else 0)
    st.write(f"**{total_feitos} de {total_itens}** itens concluídos")
    fechar_cartao()

abrir_cartao()
st.markdown("#### Finalizar")
if st.session_state.estado.get("finalizado_em"):
    st.markdown(
        f'<span class="selo-finalizado">✅ Finalizado por '
        f'{st.session_state.estado.get("finalizado_por", "")} '
        f'em {st.session_state.estado["finalizado_em"]}</span>',
        unsafe_allow_html=True,
    )
else:
    if total_feitos < total_itens:
        st.markdown(
            f'<span class="selo-pendente">⏳ Faltam {total_itens - total_feitos} itens</span>',
            unsafe_allow_html=True,
        )
    if st.button("Finalizar e salvar", type="primary"):
        operador = st.session_state.estado.get("voluntario", "").strip()
        if not operador:
            st.error("Preencha o nome do voluntário antes de finalizar.")
        else:
            registro = registrar_finalizacao(SITE, operador, total_feitos, total_itens)
            st.session_state.estado["finalizado_por"] = operador
            st.session_state.estado["finalizado_em"] = registro["data"]
            salvar_estado(SITE, st.session_state.estado)
            st.rerun()
fechar_cartao()

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

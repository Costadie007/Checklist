import streamlit as st
from streamlit_autorefresh import st_autorefresh

from banco import carregar_estado, carregar_historico
from roteiros import ROTEIROS

# Troque a senha antes de publicar.
SENHA_PAINEL = "painel2026"

st.set_page_config(page_title="Painel de acompanhamento", page_icon="📋", layout="wide")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("Painel de acompanhamento")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if senha == SENHA_PAINEL:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Senha incorreta.")
    st.stop()

# Recarrega sozinho a cada 3 segundos.
st_autorefresh(interval=3000, key="atualizacao")

st.title("Painel de acompanhamento")
st.caption("Atualiza sozinho a cada 3 segundos. Somente leitura.")

colunas = st.columns(len(ROTEIROS))

for coluna, (site, roteiro) in zip(colunas, ROTEIROS.items()):
    with coluna:
        st.subheader(roteiro["nome"])
        estado = carregar_estado(site)

        if estado is None:
            st.error("Sem conexão com o banco de dados.")
            continue

        total = sum(len(lista) for lista in roteiro["secoes"].values())
        feitos = sum(
            1 for chave, valor in estado.items()
            if chave.startswith("item-") and valor
        )
        voluntario = str(estado.get("voluntario", "")).strip()

        st.write(f"Voluntário: {voluntario or 'não informado'}")
        st.progress(feitos / total if total else 0)
        st.write(f"{feitos} de {total} concluídos")
        st.caption(f"Última alteração: {estado.get('atualizado_em', 'nenhuma ainda')}")
        if estado.get("finalizado_em"):
            st.success(
                f"Finalizado por {estado.get('finalizado_por', '')} "
                f"em {estado['finalizado_em']}"
            )

        for secao, lista in roteiro["secoes"].items():
            with st.expander(secao, expanded=True):
                for indice, texto in enumerate(lista):
                    marcado = estado.get(f"item-{secao}-{indice}", False)
                    st.write(f"{'✅' if marcado else '⬜'} {texto}")

        historico = carregar_historico(site)
        if historico:
            with st.expander("Últimas finalizações"):
                for r in historico:
                    st.write(f"{r['data']} · {r['operador']} · {r['feitos']}/{r['total']} itens")

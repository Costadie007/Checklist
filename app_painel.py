import streamlit as st
from streamlit_autorefresh import st_autorefresh

from banco import carregar_estado, carregar_historico, modo_local
from estilo import ICONES, aplicar_estilo
from roteiros import ROTEIROS

# Troque a senha antes de publicar.
SENHA_PAINEL = "painel2026"

st.set_page_config(page_title="Painel de acompanhamento", page_icon="📋", layout="wide")
aplicar_estilo("Painel de acompanhamento", "📋", "Atualiza sozinho a cada poucos segundos. Somente leitura.")

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

if modo_local():
    st.warning(
        "Banco de dados não configurado (falta FIREBASE_URL em Secrets). "
        "O painel só enxerga arquivos deste próprio site, então vai aparecer vazio."
    )

with st.sidebar:
    st.subheader("Atualização")
    intervalo = st.slider("A cada quantos segundos?", 2, 15, 3)

# Recarrega sozinho no intervalo escolhido.
st_autorefresh(interval=intervalo * 1000, key="atualizacao")

colunas = st.columns(len(ROTEIROS))

for coluna, (site, roteiro) in zip(colunas, ROTEIROS.items()):
    with coluna:
        estado = carregar_estado(site)

        st.markdown('<div class="cartao-roteiro">', unsafe_allow_html=True)
        st.markdown(f"### {ICONES.get(site, '📌')} {roteiro['nome']}")

        if estado is None:
            st.error("Sem conexão com o banco de dados.")
            st.markdown('</div>', unsafe_allow_html=True)
            continue

        total = sum(len(lista) for lista in roteiro["secoes"].values())
        feitos = sum(
            1 for chave, valor in estado.items()
            if chave.startswith("item-") and valor
        )
        voluntario = str(estado.get("voluntario", "")).strip()

        st.markdown(
            f'<span class="rotulo-voluntario">👤 {voluntario or "não informado"}</span>',
            unsafe_allow_html=True,
        )
        st.progress(feitos / total if total else 0)
        st.write(f"**{feitos} de {total}** itens concluídos")
        st.markdown(
            f'<div class="marca-tempo">Última alteração: '
            f'{estado.get("atualizado_em", "nenhuma ainda")}</div>',
            unsafe_allow_html=True,
        )

        if estado.get("finalizado_em"):
            st.markdown(
                f'<span class="selo-finalizado">✅ Finalizado por '
                f'{estado.get("finalizado_por", "")} em {estado["finalizado_em"]}</span>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<span class="selo-pendente">⏳ Em andamento</span>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

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

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from banco import carregar_estado, carregar_historico, modo_local
from roteiros import ROTEIROS

# Troque a senha antes de publicar.
SENHA_PAINEL = "painel2026"

st.set_page_config(page_title="Painel de acompanhamento", page_icon="📋", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }

    .cabecalho-painel {
        display: flex; align-items: baseline; gap: 10px; margin-bottom: 4px;
    }
    .cabecalho-painel h1 { margin: 0; font-size: 1.8rem; }
    .subtitulo-painel { color: #9db2d6; margin-bottom: 24px; }

    .cartao-roteiro {
        background: linear-gradient(160deg, #16273f 0%, #101d34 100%);
        border: 1px solid #24365a;
        border-radius: 16px;
        padding: 20px 20px 8px 20px;
        margin-bottom: 12px;
    }
    .cartao-roteiro h3 { margin: 0 0 2px 0; font-size: 1.15rem; }
    .rotulo-voluntario {
        display: inline-block; background: #1e3358; color: #bcd0f5;
        border-radius: 999px; padding: 3px 12px; font-size: 0.85rem; margin: 6px 0 12px 0;
    }
    .selo-finalizado {
        display: inline-block; background: #164a2e; color: #7fe3a4;
        border: 1px solid #2b8a52; border-radius: 999px; padding: 3px 12px;
        font-size: 0.85rem; margin-top: 6px;
    }
    .selo-pendente {
        display: inline-block; background: #4a3416; color: #f0c27b;
        border: 1px solid #8a6a2b; border-radius: 999px; padding: 3px 12px;
        font-size: 0.85rem; margin-top: 6px;
    }
    .marca-tempo { color: #7c8db3; font-size: 0.8rem; margin-top: 4px; }

    div[data-testid="stExpander"] {
        background: #101d34; border: 1px solid #24365a; border-radius: 10px;
    }
    div[data-testid="stProgress"] > div > div {
        transition: width 0.4s ease-in-out;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="cabecalho-painel">'
    '<span style="font-size:1.8rem;">📋</span><h1>Painel de acompanhamento</h1>'
    '</div>'
    '<div class="subtitulo-painel">Atualiza sozinho a cada poucos segundos. Somente leitura.</div>',
    unsafe_allow_html=True,
)

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

ICONES = {"arena": "🖥️", "holyrics": "🎤", "iluminacao": "💡"}

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

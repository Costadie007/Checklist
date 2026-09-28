import streamlit as st

# Ícone de cada site, reaproveitado no título da aba e no cabeçalho.
ICONES = {"arena": "🖥️", "holyrics": "🎤", "iluminacao": "💡"}

CSS = """
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
    margin-bottom: 16px;
}
.cartao-roteiro h3, .cartao-roteiro h4 { margin: 0 0 12px 0; }

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
div[data-testid="stProgress"] > div > div { transition: width 0.4s ease-in-out; }

div[data-testid="stTextInput"] input {
    background: #0f1c33; border: 1px solid #2a3a5c; border-radius: 8px; color: #e8edf7;
}
button[kind="primary"] { border-radius: 10px; }
button[kind="secondary"] { border-radius: 10px; }
</style>
"""


def aplicar_estilo(titulo, icone, subtitulo=""):
    """Injeta o tema azul escuro e desenha o cabeçalho da página."""
    st.markdown(CSS, unsafe_allow_html=True)
    partes = (
        '<div class="cabecalho-painel">'
        f'<span style="font-size:1.8rem;">{icone}</span><h1>{titulo}</h1>'
        '</div>'
    )
    if subtitulo:
        partes += f'<div class="subtitulo-painel">{subtitulo}</div>'
    st.markdown(partes, unsafe_allow_html=True)


def abrir_cartao():
    st.markdown('<div class="cartao-roteiro">', unsafe_allow_html=True)


def fechar_cartao():
    st.markdown('</div>', unsafe_allow_html=True)

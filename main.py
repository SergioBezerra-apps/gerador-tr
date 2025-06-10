
import streamlit as st
from rules import load_rules, evaluate_condition
from render import render_tr

st.set_page_config(page_title="Gerador de TR", layout="wide")
st.title("Gerador de Termo de Referência – TCE‑RJ")

rules = load_rules()
answers = {}

def render_field(field_name, meta):
    if meta['tipo'] == 'texto':
        return st.text_input(meta['pergunta'])
    elif meta['tipo'] == 'texto_longo':
        return st.text_area(meta['pergunta'])
    elif meta['tipo'] == 'select':
        labels = [o if isinstance(o, str) else o['label'] for o in meta['opcoes']]
        ids = [o if isinstance(o, str) else o['id'] for o in meta['opcoes']]
        choice = st.selectbox(meta['pergunta'], labels)
        return ids[labels.index(choice)]
    elif meta['tipo'] == 'radio':
        return st.radio(meta['pergunta'], meta['opcoes'])
    elif meta['tipo'] == 'boolean':
        return st.radio(meta['pergunta'], ['Sim', 'Não']) == 'Sim'
    elif meta['tipo'] == 'inteiro_opcional':
        return st.number_input(meta['pergunta'], min_value=0, step=1)
    elif meta['tipo'] == 'checklist':
        # handle outside
        return None

with st.form("tr_form"):
    for field, meta in rules['campos'].items():
        if meta['tipo'] == 'checklist':
            visible_opts = [o for o in meta['opcoes']
                            if 'visivel_se' not in o or
                            evaluate_condition(o['visivel_se'], answers)]
            labels = [o['label'] for o in visible_opts]
            selected = st.multiselect(meta['pergunta'], labels)
            for o in visible_opts:
                answers[o['id']] = o['label'] in selected
        else:
            answers[field] = render_field(field, meta)
    submitted = st.form_submit_button("Gerar TR")

if submitted:
    st.info("Gerando documentos...")
    docx_path, pdf_path = render_tr(answers)
    st.success("Arquivos gerados com sucesso!")
    with open(docx_path, "rb") as f:
        st.download_button("Baixar DOCX", f, file_name="TR.docx")
    try:
        with open(pdf_path, "rb") as f:
            st.download_button("Baixar PDF", f, file_name="TR.pdf")
    except FileNotFoundError:
        st.warning("PDF não gerado – verifique dependência do Word/LibreOffice.")

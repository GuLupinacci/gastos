import streamlit as st
import pandas as pd
from fpdf import FPDF
from io import BytesIO

st.title("Organizador de Gastos Cartão de crédito")

uploaded_file = st.file_uploader("Envie seu arquivo CSV de gastos", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df = df[df['amount'] >= 0]

    comidas = ["poke", "csc", "sushi", "burguer", "subway", "ifood", "ifd", "restaurante",
               "hamburguer", "rabodigalo", "toldo", "acai", "pizza", "cerveja", "gastronomia",
               "moochacho", "armada", "palacio china", "cookies", "hoppy"]

    def classificar_gasto(titulo):
        titulo_lower = titulo.lower()
        if "uber" in titulo_lower or "99" in titulo_lower:
            return "Uber ou 99"
        elif "lizianecristina" in titulo_lower or "ronaldo" in titulo_lower:
            return "Mercado Khomp"
        elif any(palavra in titulo_lower for palavra in comidas):
            return "Ifood, subway ou comer fora"
        elif any(palavra in titulo_lower for palavra in ["supermercados", "angeloni"]):
            return "Supermercado"
        elif any(palavra in titulo_lower for palavra in ["hbo", "spotify", "youtube", "melimais", "prime", "uol"]):
            return "Streaming"
        elif "mercadolivre" in titulo_lower:
            return "Mercado Livre"
        elif any(palavra in titulo_lower for palavra in ["gonsali", "manual"]):
            return "Cabelo"
        elif "natatorium" in titulo_lower:
            return "Academia"
        else:
            return titulo.title()

    df['categoria'] = df['title'].apply(classificar_gasto)

    tabela_final = (
        df.groupby('categoria')['amount']
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    tabela_final.index = tabela_final.index + 1
    tabela_final.rename(columns={'categoria': 'Categoria', 'amount': 'Total'}, inplace=True)

    st.write("### Resumo por categoria")
    st.dataframe(tabela_final)

    total = df['amount'].sum()
    st.write(f"**Total geral: R$ {total:.2f}**")

    # Gerar PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Resumo de Gastos por Categoria", 0, 1, "C")  # título centralizado

    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(200, 220, 255)  # cor de fundo azul claro para o cabeçalho

    # Cabeçalho da tabela
    pdf.cell(10, 10, "No", 1, 0, "C", fill=True)
    pdf.cell(120, 10, "Categoria", 1, 0, "C", fill=True)
    pdf.cell(40, 10, "Total (R$)", 1, 1, "C", fill=True)

    pdf.set_font("Arial", "", 12)

    for i, row in tabela_final.iterrows():
        pdf.cell(10, 10, str(i), 1, 0, "C")
        pdf.cell(120, 10, row['Categoria'], 1, 0)
        pdf.cell(40, 10, f"{row['Total']:.2f}", 1, 1, "R")

    # Total geral
    pdf.set_font("Arial", "B", 12)
    pdf.cell(130, 10, "Total Geral", 1, 0, "R", fill=True)
    pdf.cell(40, 10, f"R$ {total:.2f}", 1, 1, "R", fill=True)


    pdf_output = BytesIO()

    pdf_name = "resumo_gastos.pdf"
    pdf.output(pdf_name)  # salva no disco

    with open(pdf_name, "rb") as f:
        pdf_bytes = f.read()

    st.download_button(
        label="📥 Baixar resumo em PDF",
        data=pdf_bytes,
        file_name=pdf_name,
        mime="application/pdf"
    )

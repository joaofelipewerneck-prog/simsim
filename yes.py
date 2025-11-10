import streamlit as st
import datetime
import pandas as pd  # Importa a biblioteca pandas
import altair as alt # Importa a biblioteca altair

# --- FUNÇÃO AUXILIAR ---
def parse_fraction(frac_str: str) -> float:
    """
    Converte uma string de fração (ex: '1/3', '2/5') ou decimal (ex: '0.5')
    em um número float.
    """
    try:
        if "/" in frac_str:
            num, den = frac_str.strip().split('/')
            if float(den) == 0:
                return 0.0
            return float(num) / float(den)
        else:
            # Permite também a inserção de números decimais (ex: 0.5)
            return float(frac_str.strip().replace(",", "."))
    except (ValueError, TypeError, ZeroDivisionError):
        # Retorna 0.0 se a string for inválida (ex: 'abc')
        return 0.0

# --- INÍCIO DA APLICAÇÃO ---
st.set_page_config(layout="wide")

# --- ADIÇÃO DA LOGO AQUI ---
st.image("logo_fgv_dosimetria.png", width=200) # Verifique se este arquivo existe

st.title("⚖️ Calculadora de Dosimetria da Pena")
st.markdown("Simulador do Método Trifásico (Art. 68 do Código Penal)")

# --- CRIAÇÃO DAS ABAS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏁 Penas Cominadas", 
    "1️⃣ Fase 1: Pena-Base", 
    "2️⃣ Fase 2: Pena-Provisória", 
    "3️⃣ Fase 3: Pena Definitiva",
    "📊 Resultado Final"
])


# --- ABA 1: PENAS COMINADAS E TERMO MÉDIO ---
with tab1:
    st.header("Penas Cominadas e Termo Médio")

    tipo_crime = st.radio(
        "O crime é Simples ou Qualificado?",
        ("Simples", "Qualificado"),
        horizontal=True,
        help="Se for qualificado, as penas anteriores serão desconsideradas."
    )

    if tipo_crime == "Simples":
        col1, col2 = st.columns(2)
        with col1:
            pena_minima_cominada = st.number_input(
                "Pena MÍNIMA cominada (em anos):",
                min_value=0.0, value=1.0, step=0.1, format="%.2f"
            )
        with col2:
            pena_maxima_cominada = st.number_input(
                "Pena MÁXIMA cominada (em anos):",
                min_value=pena_minima_cominada, value=4.0, step=0.1, format="%.2f"
            )
    else:
        st.info("Informe as novas penas para o crime qualificado.")
        col1, col2 = st.columns(2)
        with col1:
            pena_minima_cominada = st.number_input(
                "Nova Pena MÍNIMA cominada (em anos):",
                min_value=0.0, value=2.0, step=0.1, format="%.2f", key="min_qual"
            )
        with col2:
            pena_maxima_cominada = st.number_input(
                "Nova Pena MÁXIMA cominada (em anos):",
                min_value=pena_minima_cominada, value=8.0, step=0.1, format="%.2f", key="max_qual"
            )

    if pena_maxima_cominada < pena_minima_cominada:
        st.error("A pena máxima não pode ser menor que a pena mínima.")
        st.stop()

    termo_medio = (pena_maxima_cominada + pena_minima_cominada) / 2
    st.metric("Termo Médio:", f"{termo_medio:.2f} anos")


# --- ABA 2: FASE 1: PENA-BASE ---
with tab2:
    st.header("1ª Fase: Pena-Base (Circunstâncias Judiciais - Art. 59)")

    circunstancias = [
        "Culpabilidade", "Antecedentes", "Conduta Social", "Personalidade do agente",
        "Motivos do crime", "Circunstâncias do crime", "Consequências do crime",
        "Comportamento da vítima"
    ]

    negativas = []
    st.write("Selecione as circunstâncias judiciais valoradas negativamente:")

    cols_fase1 = st.columns(4)
    for i, circ in enumerate(circunstancias):
        if cols_fase1[i % 4].checkbox(circ):
            negativas.append(circ)

    count_negativas = len(negativas)
    st.info(f"**Total de circunstâncias negativas:** {count_negativas}")

    pena_base = pena_minima_cominada
    intervalo_pena = pena_maxima_cominada - pena_minima_cominada

    if 0 < count_negativas <= 3:
        st.subheader("Cálculo para 1-3 circunstâncias negativas")
        fracao_tipo = st.radio(
            "Escolha a fração de aumento por circunstância:",
            ("1/8", "1/6"),
            key="fase1_frac",
            horizontal=True
        )

        if fracao_tipo == "1/8":
            aumento_por_circunstancia = (1/8) * intervalo_pena
        else:
            aumento_por_circunstancia = (1/6) * intervalo_pena

        aumento_total = aumento_por_circunstancia * count_negativas
        pena_base = pena_minima_cominada + aumento_total

        st.write(f"Intervalo da pena: {intervalo_pena:.2f} anos")
        st.write(f"Aumento por circunstância ({fracao_tipo}): {aumento_por_circunstancia:.2f} anos")
        st.write(f"Aumento total ({count_negativas}x): {aumento_total:.2f} anos")

    elif count_negativas >= 4:
        st.subheader("Cálculo para 4+ circunstâncias negativas (Conjunto Desvalioso)")
        st.info("Para 4 ou mais circunstâncias (ou todas as 8), a pena-base deve se aproximar ou se igualar ao Termo Médio.")
        pena_base = termo_medio

    if pena_base > pena_maxima_cominada:
        pena_base = pena_maxima_cominada
    if pena_base < pena_minima_cominada:
        pena_base = pena_minima_cominada

    st.metric("Pena-Base (Resultado da 1ª Fase):", f"{pena_base:.2f} anos")


# --- ABA 3: FASE 2: PENA-PROVISÓRIA ---
with tab3:
    st.header("2ª Fase: Pena-Provisória (Atenuantes e Agravantes)")

    pena_provisoria = pena_base

    col3, col4 = st.columns(2)
    with col3:
        num_atenuantes = st.number_input(
            "Informe o número de ATENUANTES:", min_value=0, step=1
        )
    with col4:
        num_agravantes = st.number_input(
            "Informe o número de AGRAVANTES:", min_value=0, step=1
        )

    modificador_legal = (1/6) * pena_base
    st.info(f"Valor do modificador (1/6 da Pena-Base): {modificador_legal:.2f} anos")

    diferenca_circunstancias = num_agravantes - num_atenuantes

    if diferenca_circunstancias > 0:
        aumento = modificador_legal * diferenca_circunstancias
        pena_provisoria = pena_base + aumento
        st.write(f"Preponderância de {diferenca_circunstancias} agravante(s): Aumento de {aumento:.2f} anos")
    elif diferenca_circunstancias < 0:
        reducao = modificador_legal * abs(diferenca_circunstancias)
        pena_provisoria = pena_base - reducao
        st.write(f"Preponderância de {abs(diferenca_circunstancias)} atenuante(s): Redução de {reducao:.2f} anos")
    else:
        st.write("Agravantes e atenuantes se compensaram. A pena permanece inalterada.")
        pena_provisoria = pena_base

    if pena_provisoria > pena_maxima_cominada:
        pena_provisoria = pena_maxima_cominada
        st.warning("Pena provisória limitada à pena máxima cominada.")
    if pena_provisoria < pena_minima_cominada:
        pena_provisoria = pena_minima_cominada
        st.warning("Pena provisória limitada à pena mínima cominada (Súmula 231, STJ).")

    st.metric("Pena Provisória (Resultado da 2ª Fase):", f"{pena_provisoria:.2f} anos")


# --- ABA 4: FASE 3: PENA DEFINITIVA ---
with tab4:
    st.header("3ª Fase: Pena Definitiva (Causas de Aumento e Diminuição)")
    st.info("A ordem de cálculo é: 1º) Causas de Aumento, 2º) Causas de Diminuição.")

    pena_definitiva = pena_provisoria
    
    # CORREÇÃO DO SYNTAX ERROR: Removido o espaço
    pena_apos_aumento = pena_provisoria

    st.subheader("Causas de Aumento (Gerais e Especiais)")
    tem_aumento = st.radio("Há causas de AUMENTO?", ("Não", "Sim"), horizontal=True, key="radio_aum")

    fracao_aumento_total = 0.0
    if tem_aumento == "Sim":
        num_aumentos = st.number_input("Quantas causas de aumento?", min_value=1, value=1, step=1, key="num_aum")
        for i in range(num_aumentos):
            frac_str = st.text_input(
                f"Fração de aumento {i+1} (ex: '1/3', '2/3', '0.5'):",
                key=f"aum_{i}"
            )
            fracao_aumento_total += parse_fraction(frac_str)

    if fracao_aumento_total > 0:
        aumento_3fase = pena_provisoria * fracao_aumento_total
        pena_apos_aumento = pena_provisoria + aumento_3fase
        st.write(f"Fração total de aumento: {fracao_aumento_total:.2f} ({fracao_aumento_total*100:.0f}%)")
        st.write(f"Aumento aplicado: +{aumento_3fase:.2f} anos")
        st.write(f"**Pena após aumento:** {pena_apos_aumento:.2f} anos")
    else:
        pena_apos_aumento = pena_provisoria

    st.subheader("Causas de Diminuição (Gerais e Especiais)")
    tem_diminuicao = st.radio("Há causas de DIMINUIÇÃO?", ("Não", "Sim"), horizontal=True, key="radio_dim")

    fracao_diminuicao_total = 0.0
    if tem_diminuicao == "Sim":
        num_diminuicoes = st.number_input("Quantas causas de diminuição?", min_value=1, value=1, step=1, key="num_dim")
        for i in range(num_diminuicoes):
            frac_str = st.text_input(
                f"Fração de diminuição {i+1} (ex: '1/3', '1/2'):",
                key=f"dim_{i}"
            )
            fracao_diminuicao_total += parse_fraction(frac_str)

    if fracao_diminuicao_total > 0:
        reducao_3fase = pena_apos_aumento * fracao_diminuicao_total
        pena_definitiva = pena_apos_aumento - reducao_3fase
        st.write(f"Fração total de diminuição: {fracao_diminuicao_total:.2f} ({fracao_diminuicao_total*100:.0f}%)")
        st.write(f"Redução aplicada: -{reducao_3fase:.2f} anos")
    else:
        pena_definitiva = pena_apos_aumento

    if pena_definitiva < 0:
        pena_definitiva = 0.0

    st.metric("Pena Definitiva (Resultado da 3ª Fase):", f"{pena_definitiva:.2f} anos")

# --- ABA 5: RESULTADO FINAL ---
with tab5:
    st.header("Análise Final: Regime e Substituição")

    # --- Fixação do Regime ---
    st.subheader("Fixação do Regime Penal (Art. 33 CP)")

    regime = "Indefinido"
    reincidente = st.radio("O réu é reincidente?", ("Não", "Sim"), horizontal=True, key="regime_reinc") == "Sim"

    if pena_definitiva > 8:
        regime = "FECHADO"
    elif pena_definitiva > 4:
        regime = "FECHADO" if reincidente else "SEMIABERTO"
    else:
        if reincidente:
            if count_negativas == 0:
                regime = "SEMIABERTO (Súmula 269, STJ)"
            else:
                regime = "SEMIABERTO (podendo ser Fechado se circ. judiciais desfavoráveis)"
        else:
            regime = "ABERTO"

    if count_negativas == 0 and not reincidente and regime != "ABERTO" and pena_definitiva <= 4:
        regime = "ABERTO"
        st.info("Súmula 440 STJ: Pena-base no mínimo legal e réu primário. Regime ABERTO é o aplicável.")

    st.metric("Regime Inicial de Cumprimento Sugerido:", regime)
    st.write("---")

    # Simplifica o regime calculado para bater com os gráficos
    regime_simplificado = "Indefinido"
    if "FECHADO" in regime.upper():
        regime_simplificado = "Fechado"
    elif "SEMIABERTO" in regime.upper():
        regime_simplificado = "Semiaberto"
    elif "ABERTO" in regime.upper():
        regime_simplificado = "Aberto"

    # --- NOVO GRÁFICO DE ROSCA (DADOS DO CNJ) ---
    st.subheader("Contexto: População em Execução Penal por Regime (Fonte: CNJ)")
    st.markdown("""
    O gráfico de rosca abaixo utiliza dados públicos do **Painel CNJ** (referentes à execução penal) para contextualizar o resultado.
    """)

    # 1. Dados extraídos do Painel CNJ (Execução Penal, 1º Grau)
    data_cnj = {
        'Regime': ['Fechado', 'Semiaberto', 'Aberto', 'Medida de Segurança'],
        'NumeroDePessoas': [341282, 161026, 111417, 25590],
        'Porcentagem': [53.4, 25.2, 17.4, 4.0]
    }
    df_cnj = pd.DataFrame(data_cnj)

    # 2. Adiciona destaque
    df_cnj['Destaque'] = df_cnj['Regime'].apply(
        lambda x: 'Resultado Deste Caso' if x == regime_simplificado else 'Outros Regimes'
    )

    # 3. Cria o gráfico de rosca (Donut Chart)
    base = alt.Chart(df_cnj).encode(
       theta=alt.Theta("Porcentagem", stack=True)
    )

    # Camada da rosca
    pie = base.mark_arc(outerRadius=120, innerRadius=80).encode(
        color=alt.Color('Destaque',
                        scale=alt.Scale(
                            domain=['Resultado Deste Caso', 'Outros Regimes'],
                            range=['#FF4B4B', '#909090'] # Vermelho para destaque, cinza para outros
                        ),
                        legend=alt.Legend(title="Legenda")
                       ),
        order=alt.Order('Porcentagem', sort='descending'),
        tooltip=['Regime', 'NumeroDePessoas', alt.Tooltip('Porcentagem', format='.1f')]
    ).properties(
        title="Distribuição de Pessoas por Regime (Fonte: CNJ)"
    )

    # Camada de texto (porcentagens)
    text = base.mark_text(radius=140).encode(
        text=alt.Text('Porcentagem', format=".1f"),
        order=alt.Order('Porcentagem', sort='descending'),
        color=alt.value("black") # Cor do texto
    )
    
    chart_donut = pie + text
    
    # 4. Exibe o gráfico
    st.altair_chart(chart_donut, use_container_width=True)

    # 5. Adiciona o texto de contexto
    if regime_simplificado != "Indefinido" and regime_simplificado in df_cnj['Regime'].values:
        # Puxa os dados do regime calculado para o texto
        dados_regime = df_cnj[df_cnj['Regime'] == regime_simplificado].iloc[0]
        st.info(f"""
        **Adequação:** O seu caso se enquadra no **{dados_regime['Regime']}**. 
        Nos dados do CNJ, esta categoria representa **{dados_regime['Porcentagem']}%** do total, 
        correspondendo a **{dados_regime['NumeroDePessoas']:,.0f}** pessoas.
        """.replace(",", ".")) # Formata o número (10000 -> 10.000)
    
    st.write("---")
    # --- FIM DO GRÁFICO DE ROSCA ---


    # --- GRÁFICO DE BARRAS (Fictício) ---
    st.subheader("Contexto Estatístico (Dados Fictícios)")

    # 1. Cria o banco de dados fictício
    data_ficticio = {'Regime': ['Aberto', 'Semiaberto', 'Fechado'],
                     'Porcentagem': [45, 35, 20]}
    df_ficticio = pd.DataFrame(data_ficticio)

    # 2. Adiciona uma coluna para o destaque
    df_ficticio['Destaque'] = df_ficticio['Regime'].apply(
        lambda x: 'Resultado Deste Caso' if x == regime_simplificado else 'Média Geral'
    )

    # 3. Cria o gráfico com Altair
    chart_bar = alt.Chart(df_ficticio).mark_bar().encode(
        x=alt.X('Regime', sort=None),
        y=alt.Y('Porcentagem', title='Porcentagem de Casos (%)'),
        color=alt.Color('Destaque',
                        scale=alt.Scale(
                            domain=['Resultado Deste Caso', 'Média Geral'],
                            range=['#FF4B4B', '#909090']
                        ),
                        legend=alt.Legend(title="Legenda")
                       ),
        tooltip=['Regime', 'Porcentagem']
    ).properties(
        title="Posicionamento do Caso na Média Fictícia de Regimes"
    )

    # 4. Exibe o gráfico no Streamlit
    st.altair_chart(chart_bar, use_container_width=True)
    st.write("---")
    
    # --- Substituição da Pena ---
    st.subheader("Substituição da Pena (Art. 44 CP)")
    st.write("Responda aos requisitos para análise da substituição:")

    req1_bool = (pena_definitiva <= 4)
    st.checkbox(
        f"Requisito 1: Pena aplicada é igual ou inferior a 4 anos? (Resultado: {pena_definitiva:.2f} anos)",
        value=req1_bool,
        disabled=True
    )
    req2_bool = st.radio(
        "Requisito 2: O crime foi cometido SEM violência ou grave ameaça à pessoa?",
        ("Sim", "Não")
    ) == "Sim"
    req3_bool = st.radio(
        "Requisito 3: O réu é NÃO reincidente em crime doloso?",
        ("Sim", "Não")
    ) == "Sim"
    req4_bool = st.radio(
        "Requisito 4: As circunstâncias judiciais (Art. 59) indicam que a substituição é suficiente?",
        ("Sim", "Não")
    ) == "Sim"

    elegivel = False
    if req1_bool and req2_bool and req3_bool and req4_bool:
        elegivel = True
    elif req1_bool and req2_bool and not req3_bool:
        st.info("O réu é reincidente, mas a substituição AINDA PODE ser possível (Art. 44, § 3º).")
        excecao_reincidente = st.checkbox("A medida é socialmente recomendável E a reincidência não se operou pelo mesmo crime?")
        if excecao_reincidente and req4_bool:
            elegivel = True

    if elegivel:
        st.success("✅ SIM, o condenado é elegível para a Substituição da Pena Privativa de Liberdade (PPL) por Restritiva de Direitos (PRD).")
    else:
        st.error("❌ NÃO, o condenado NÃO é elegível para a substituição da pena.")

    st.markdown("---")
    st.markdown("""
    **Aviso Legal:** Esta é uma ferramenta de simulação e aprendizado, baseada nas regras gerais do Código Penal Brasileiro e em Súmulas de tribunais superiores. Ela não substitui a análise de um juiz ou advogado, que considera a totalidade e as nuances do caso concreto. As interpretações (como o valor da fração na 1ª fase) podem variar.
    """)



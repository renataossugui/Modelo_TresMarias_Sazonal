# **PDM - Probabilistic-distributed Model** 
# 
# **Autora:** Adriana Cuartas <adriana.cuartas@cemaden.gov.br>  
# **Modificações:** Eduardo Luz (DEZ/2014), Luiz Valério de Castro Carvalho, Rong Zhang  

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# **Configurações Iniciais**

PLOTARGRAFICOS = 1
ESTATISTICAS = 1

areabacia3 = 51009045523.
fator = areabacia3 / (1000. * 86400.)  # area da bacia em m2

INICIOEST = 11231  # periodo do calculo das estatísticas entre "01/Out/2013" até presente

# **Leitura de ARQUIVOS DE PRECIPITACAO, EVAPORACAO e VAZAO OBSERVADOS**

PATH = r'C:\Users\yurio\Downloads\ProjetoSaberPardo\ProjetoSaberPardo\ModeloHidrologico-PDM'
os.chdir(PATH)

# contando com dias simulacao + previsao Eta propriamente dia
diasPrevisaoChuva = 14

# VETOR DAS VAZOES FUTURAS PARA A PLANILHA "Previsao"
QFUTURAS = np.zeros((34, diasPrevisaoChuva))
contQFUTURAS = 0


# **Bloco de Leitura do Passado**
df_passado = pd.read_csv('PEQ_SaoFrancisco_TresMarias_passado.csv', sep=';')
df_passado.columns = df_passado.columns.str.lower().str.replace(' ', '')
numdad = len(df_passado)

date_past = df_passado['dia'].values 
rainfall = df_passado['prec(mm)'].values.astype(float)
evp_past = df_passado['evapora_hs2003'].values.astype(float) 
QNat_past = df_passado['qnat'].values.astype(float)

# Construção da matriz rainfall1 e evp_past de 34 membros
# 32 linhas (índices de 0 a 31) duplicando exatamente a mesma série de precipitação observada (rainfall)
rainfall1 = np.zeros((34, len(df_passado))) #TODO por que 34 se temos somente 31 membros?
for idx in range(32):
    rainfall1[idx, :] = rainfall[:]

# Março a setembro critico (2007) e na sequencia ano critico (2014).
# Para a simulação em 2019, considera-se a precipitação de 2014.
rainfall1[32, :] = rainfall[:]

# série sintética com mínimos históricos mensais -
# coluna V aba minimos da planilha de monitoramento da precipitação
rainfall1[33, :] = rainfall[:]




# **LE ARQUIVOS DE PRECIPITACAO, EVAPORACAO PREVISTOS**

# Substitui o WHILE NOT EOF(15), strsplit e a montagem manual da MATRIZ2
df_futuro = pd.read_csv('PE_SaoFrancisco_TresMarias_futuro.csv', sep=';')
df_futuro.columns = df_futuro.columns.str.lower().str.replace(' ', '')
numdad2 = len(df_futuro)

# <alice;karinne> alterecao matriz de 8 (ETA) para 21 (GEFS) membros de previsao de precipitação
date_prev = df_futuro['data'].values 

# Array de cada coluna do arquivo futuro
evp_prev = df_futuro['etp'].values.astype(float)
QDefluencia_prev = df_futuro['qdefluencia(ons+2025)+qvert'].values.astype(float)
QExtracao_prev = df_futuro['qext'].values.astype(float)
rainseriePcritica = df_futuro['pcritico_mar-set2021+anocritico2014'].values.astype(float)
rainserieP_minima_mensal = df_futuro['cenarioprecminimamensal'].values.astype(float)

# constroi um array onde cada linha representa um membro de previsão de precipitação (de 0 a 31)
# e cada coluna representa um dia de previsão
rainprev1 = np.zeros((34, len(df_futuro)))
for idx in range(31):
    rainprev1[idx, :] = df_futuro.iloc[:, idx + 1].values.astype(float)

QExt = QDefluencia_prev + QExtracao_prev  # (Qdefluencia(ONS+2025)+Qvert) + Qext
rainprev1[32, :] = rainseriePcritica  # Pcritico_mar-set2021+AnoCritico2014	
rainprev1[33, :] = rainserieP_minima_mensal  # Cenario prec minima mensal

# **INICIO DATA DE 1983 A 2026*

# TODO soma o número de dias do passado e do futuro, subtraindo 2 para não contar o dia inicial e final duas vezes
numdad3 = numdad + numdad2 

datasazostring = np.concatenate([date_past, date_prev])
datasazo_dt = pd.to_datetime(datasazostring, format='%d/%m/%Y')



# **INDICE SAZONAL**
sazoindex = np.ones(numdad3)  # 1 = ESTAÇÃO CHUVOSA
months = datasazo_dt.month
sazoindex[(months >= 4) & (months <= 9)] = 0  # 0 = ESTAÇÃO SECA
# 2 = ESTAÇÃO TRANSIÇÃO
# SECA = abril-setembro, TRANSIÇÃO= março e outubro, WET= novembro-fevereiro

# **PARAMETROS CALIBRACAO INICIAIS**
Sginio = 8.0
deltat = 24. / 24.

# **FILTRO ECKHARDT**
BFImax = 0.874722428
BFIa = 0.863085259

# COMENTARIOS DO CODIGO EM IDL
# openw,80,'teste.txt'SAIDA PARA VALIDAR A SAZONALIDADE DA CALIBRACAO
# PARÂMETROS
# ----------------------------------------------------------------------------------------------------------------------
# Última calibração da Rong
#     Cmax           Cmin           b          1/kg        1/kb            k1           k2
#  WET=[1037.631,      53.906,       0.419,     968.466,    1632.931,       3.060,       5.709]
#  DRY=[947.933,      102.150,       0.171,     999.190,    3776.459,       2.370,      11.992]
# ----------------------------------------------------------------------------------------------------------------------
# Modificação Lis para melhorar calibração, vazão dos cenários estavam baixando muito na estação chuvosa FEV/2019

#  WET=[1504.7,      156.5,       0.46,     1038.1,    3361.5,       2.00,      7.49]
#  DRY=[1416.6,      162.1,       0.16,      930.1,    2483.6,       4.00,      7.84]
# ----------------------------------------------------------------------------------------------------------------------
# Modificação Adriana para melhorar calibração, vazão simulada estava consideravelmente subestimada 02/FEV/2021
# Combinação das calibrações de Rong e Lis
# 08 de junho de 2021 - perfeita para estação seca
#
# WET=[1037.631,      53.906,       0.239,    1038.466,    2032.931,       2.060,       5.490]
# DRY=[947.933,      112.150,       0.181,    809.190,    3476.459,       4.370,       8.840]

# 07 de março de 2022: Adriana
# WET=[1234.7,      96.5,     0.288,     808.466,    2002.931,     2.760,     5.490]
# DRY=[967.9,       52.2,     0.141,     709.190,    2276.459,     4.070,     8.092]

WET = np.array([1504.7, 156.5, 0.420, 638.47, 3061.5, 2.00, 5.49])
DRY = np.array([947.9, 92.2, 0.191, 709.19, 3076.5, 4.37, 8.84])

TST = (WET + DRY) / 2

# #### INICIO DO LOOP DOS MEMBROS DE PRECIPITACAO PARA PREVISÃO <alice;karinne>

# Loop **N** (Membros 0 a 31): Aplica a precipitação prevista de cada membro (0 a 31) para simular cenários de vazão.  
# Loop **j** (Cenários 0 a 6): Aplica os multiplicadores de precipitação para simular cenários (-75% a +50%).   
# Loop **i** (Tempo 0 a numdad3): Executa o passo a passo diário da simulação do PDM  
# Leitura e Balanço do Reservatório: Acontece logo depois que o loop **i** termina.  
# 
# Loop **k** (Evolução do Reservatório): Roda a projeção de volume acumulado.  
# **Fechamento de tudo**: Os arquivos individuais (TM_Q_ResulCalib, TM_V_Sim) e os gráficos são gerados e salvos antes do fim do grande loop N.

# ==============================================================================
# FOR N=0,33 - LOOP DOS MEMBROS DE PRECIPITACAO FUTURO
# ==============================================================================
for N in range(34):

    #CALCULO DO BALANCO DO MODELO HIDROLÓGICO   

    etr = np.zeros(numdad3)
    di = np.zeros(numdad3)
    St = np.zeros(numdad3)
    Pefect = np.zeros(numdad3)
    Ct = np.zeros(numdad3)
    V = np.zeros(numdad3)
    Sgt = np.zeros(numdad3)
    Qb = np.zeros(numdad3)
    Qbtrans = np.zeros(numdad3)
    Qdtrans = np.zeros(numdad3)
    qt = np.zeros(numdad3)
    Qtotal = np.zeros(numdad3)
    Stotal = np.zeros(numdad3)

    evaptotal = np.concatenate([evp_past, evp_prev])      # EVAPOTRANSPIRAÇÃO POTENCIAL OBSERVADA + PREVISTA MÉDIA

    rainprevMEMBROS = rainprev1[N, :] #chuva prevista 31 membros
    rainfall1MEMBROS = rainfall1[N, :] #chuva observada 1 membro (rainfall)

    Pprev75menos = np.zeros(numdad2)
    Pprev50menos = np.zeros(numdad2)
    Pprev30menos = np.zeros(numdad2)
    Pprev25menos = np.zeros(numdad2)
    Pprevmedia = np.zeros(numdad2)
    Pprev25mais = np.zeros(numdad2)
    Pprev50mais = np.zeros(numdad2)
    
    # mantem os 14 primeiros dias de chuva previstos (diasPrevisaoChuva) sem alteração, 
    # e aplica os multiplicadores a partir do 15º dia
    # j=0 Alteração em 18 Jan 2018; Série mais pessimista que o P-50%, mas mais otimista que P-75%
    Pprev75menos[:] = np.concatenate([rainprevMEMBROS[0:diasPrevisaoChuva], rainprevMEMBROS[diasPrevisaoChuva:] * 0.40]) 
    Pprev50menos[:] = np.concatenate([rainprevMEMBROS[0:diasPrevisaoChuva], rainprevMEMBROS[diasPrevisaoChuva:] * 0.50]) 
    Pprev30menos[:] = np.concatenate([rainprevMEMBROS[0:diasPrevisaoChuva], rainprevMEMBROS[diasPrevisaoChuva:] * 0.70]) 
    Pprev25menos[:] = np.concatenate([rainprevMEMBROS[0:diasPrevisaoChuva], rainprevMEMBROS[diasPrevisaoChuva:] * 0.75])
    Pprevmedia[:]   = np.concatenate([rainprevMEMBROS[0:diasPrevisaoChuva], rainprevMEMBROS[diasPrevisaoChuva:]])        
    Pprev25mais[:]  = np.concatenate([rainprevMEMBROS[0:diasPrevisaoChuva], rainprevMEMBROS[diasPrevisaoChuva:] * 1.25])
    Pprev50mais[:]  = np.concatenate([rainprevMEMBROS[0:diasPrevisaoChuva], rainprevMEMBROS[diasPrevisaoChuva:] * 1.50])

    rain75menos = np.concatenate([rainfall1MEMBROS, Pprev75menos]) #PRECIPITAÇÃO OBSERVADA + PREVISTA 75 ABAIXO DA MÉDIA
    rain50menos = np.concatenate([rainfall1MEMBROS, Pprev50menos]) #PRECIPITAÇÃO OBSERVADA + PREVISTA 50 ABAIXO DA MÉDIA
    rain30menos = np.concatenate([rainfall1MEMBROS, Pprev30menos]) #PRECIPITAÇÃO OBSERVADA + PREVISTA 30 ABAIXO DA MÉDIA
    rain25menos = np.concatenate([rainfall1MEMBROS, Pprev25menos]) #PRECIPITAÇÃO OBSERVADA + PREVISTA 25 ABAIXO DA MÉDIA
    rainmedia   = np.concatenate([rainfall1MEMBROS, Pprevmedia])
    rain25mais  = np.concatenate([rainfall1MEMBROS, Pprev25mais])  #PRECIPITAÇÃO OBSERVADA + PREVISTA 25 ACIMA DA MÉDIA
    rain50mais  = np.concatenate([rainfall1MEMBROS, Pprev50mais])  #PRECIPITAÇÃO OBSERVADA + PREVISTA 50 ACIMA DA MÉDIA

    # array com 7 linhas, onde cada linha irá armazenar um cenário completo de precipitação (passado + futuro).
    raintotal = np.zeros((7, numdad3))
    Qcenarios = np.zeros((7, numdad3))
    ETRcenarios = np.zeros((7, numdad3))
    Scenarios = np.zeros((7, numdad3))
    Qbasecen = np.zeros((7, numdad3))
    Qsuperfcen = np.zeros((7, numdad3))
    
    # cada linha do array raintotal recebe um cenário completo de precipitação (passado + futuro) 
    # para cada cenário de precipitação
    raintotal[0, :] = rain75menos[:] 
    raintotal[1, :] = rain50menos[:]
    raintotal[2, :] = rain30menos[:]
    raintotal[3, :] = rain25menos[:]
    raintotal[4, :] = rainmedia[:]
    raintotal[5, :] = rain25mais[:]
    raintotal[6, :] = rain50mais[:]

    #--------------------------------------------
    BFIQbi = np.zeros(numdad3)

    # ==========================================================================
    # FOR j=0,6 - LOOP PARA OS CENÁRIOS DE PRECIPITAÇÃO
    # ==========================================================================
    for j in range(7):
        
        #PARÂMETROS
        #ESTACAO CHUVOSA
        Cmax = WET[0]
        Cmin = WET[1]
        b = WET[2]
        kg = 1 / WET[3]
        kb = 1 / WET[4]
        k1 = WET[5] * 24. / 24.
        k2 = WET[6] * 24. / 24.
        #===============================
        Smax = (b * Cmin + Cmax) / (b + 1.)
        Smin = 0.55 * Smax
        Stinio = Smin * 1.25
        Stini = Stinio
        Sgini = Sginio # Stini = Stinio & Sgini = Sginio

        FlagMohor = 1 # 1 maximo iteracoes correcao State Update
        corregeAnterior = 100.0

        # ======================================================================
        # FOR i=0,numdad3 - LOOP DIÁRIO
        # ======================================================================
        for i in range(numdad3):

            if i > 0 and sazoindex[i] != sazoindex[i-1]: # IF i GT 0 AND sazoindex(i) NE sazoindex(i-1) THEN BEGIN

                if sazoindex[i] == 0: # ESTACAO SECA
                    Cmax = DRY[0]     # multiplicar por um valor maior que 1 faz aumentar vazão
                    Cmin = DRY[1]
                    b = DRY[2]
                    kg = 1 / DRY[3]
                    kb = 1 / DRY[4]
                    k1 = DRY[5] * 24. / 24.
                    k2 = DRY[6] * 24. / 24.

                if sazoindex[i] == 1: # ESTACAO CHUVOSA
                    Cmax = WET[0]
                    Cmin = WET[1]
                    b = WET[2]
                    kg = 1 / WET[3]
                    kb = 1 / WET[4]
                    k1 = WET[5] * 24. / 24.
                    k2 = WET[6] * 24. / 24.

                if sazoindex[i] == 2: # ESTACAO TRANSIÇÃO
                    Cmax = TST[0]
                    Cmin = TST[1]
                    b = TST[2]
                    kg = 1 / TST[3]
                    kb = 1 / TST[4]
                    k1 = TST[5] * 24. / 24.
                    k2 = TST[6] * 24. / 24.


            # Aqui são adjustments mensais na calibração, pequenos adjustments mensais para melhorar a performance do PDM
            
            # Estação Chuvosa
            # IF ( ( (DATASAZO(0,I) EQ 01) AND (DATASAZO(1,I) EQ 01)) AND ((DATASAZO(2,I) EQ 26) OR (DATASAZO(2,I) EQ 2026)) ) THEN BEGIN
            # Cmax = WET[0]*0.75;0.85; aqui aumentei a vazão em janeiro
            # Cmin = WET[1]
            # b = WET[2]
            # kg = 1/WET[3]
            # kb = 1/WET[4]
            # k1 = WET[5]*24./24.
            # k2 = WET[6]*24./24.
            # ENDIF
            # 
            # IF ( ( (DATASAZO(0,I) EQ 01) AND (DATASAZO(1,I) EQ 02)) AND ((DATASAZO(2,I) EQ 26) OR (DATASAZO(2,I) EQ 2026)) ) THEN BEGIN
            # Cmax = WET[0]*0.76;0.805; aqui aumentei a vazão em fev
            # Cmin = WET[1]
            # b = WET[2]
            # kg = 1/WET[3]
            # kb = 1/WET[4]
            # k1 = WET[5]*24./24.
            # k2 = WET[6]*24./24.
            # ENDIF
            # 
            # IF ( ( (DATASAZO(0,I) EQ 01) AND (DATASAZO(1,I) EQ 03)) AND ((DATASAZO(2,I) EQ 26) OR (DATASAZO(2,I) EQ 2026)) ) THEN BEGIN
            # Cmax = WET[0]*0.94;0.98; aqui aumentei a vazão em mar
            # Cmin = WET[1]
            # b = WET[2]
            # kg = 1/WET[3]
            # kb = 1/WET[4]
            # k1 = WET[5]*24./24.
            # k2 = WET[6]*24./24.
            # ENDIF
            
            # Equivalente em Python se fossem descomentados (utilizando as propriedades do Pandas datetime):
            # current_date = datasazo_dt[i]
            # if current_date.day == 1 and current_date.month == 1 and (current_date.year == 26 or current_date.year == 2026):
            #     Cmax = WET[0] * 0.75
            #     Cmin = WET[1]
            #     b = WET[2]
            #     kg = 1 / WET[3]
            #     kb = 1 / WET[4]
            #     k1 = WET[5] * 24. / 24.
            #     k2 = WET[6] * 24. / 24.

            # Estação Seca
            # se for o dia 1 de maio de 2026, ajusta os parâmetros para a estação seca
            if (datasazo_dt[i].day == 1) and (datasazo_dt[i].month == 5) and ((datasazo_dt[i].year == 26) or (datasazo_dt[i].year == 2026)):
                Cmax = DRY[0] * 1.065 #1.05
                Cmin = DRY[1]
                b = DRY[2]
                kg = 1 / DRY[3]
                kb = 1 / DRY[4]
                k1 = DRY[5] * 24. / 24.
                k2 = DRY[6] * 24. / 24.
            
            # se for o dia 1 de julho de 2026, ajusta os parâmetros para a estação seca
            if (datasazo_dt[i].day == 1) and (datasazo_dt[i].month == 7) and ((datasazo_dt[i].year == 26) or (datasazo_dt[i].year == 2026)):
                Cmax = DRY[0] * 0.85 #0.70 aumentei em julho pra frente
                Cmin = DRY[1]
                b = DRY[2]
                kg = 1 / DRY[3]
                kb = 1 / DRY[4]
                k1 = DRY[5] * 24. / 24.
                k2 = DRY[6] * 24. / 24.
            
            # se for o dia 1 de setembro de 2026, ajusta os parâmetros para a estação seca
            if (datasazo_dt[i].day == 1) and (datasazo_dt[i].month == 9) and ((datasazo_dt[i].year == 26) or (datasazo_dt[i].year == 2026)):
                Cmax = DRY[0] * 0.70 #0.5 aumentei ainda mais em setembro
                Cmin = DRY[1]
                b = DRY[2]
                kg = 1 / DRY[3]
                kb = 1 / DRY[4]
                k1 = DRY[5] * 24. / 24.
                k2 = DRY[6] * 24. / 24.

            Smax = (b * Cmin + Cmax) / (b + 1.)
            Smin = 0.45 * Smax
            delta1a = np.exp(-deltat / k1)
            delta2a = np.exp(-deltat / k2)
            delta1 = -(delta1a + delta2a)
            delta2 = delta1a * delta2a
            w0 = (k1 * (delta1a - 1.) - k2 * (delta2a - 1.)) / (k2 - k1)
            w1 = (k2 * delta1a * (delta2a - 1.) - k1 * delta2a * (delta1a - 1.)) / (k2 - k1)

            St[i] = Stini
            # Added by Rong
            if St[i] > Smax: St[i] = Smax
            
            Ct[i] = Cmin + (Cmax - Cmin) * (1 - ((Smax - St[i]) / (Smax - Cmin)) ** (1. / (b + 1.)))
            etr[i] = (1. - ((Smax - St[i]) / Smax) ** 1.0) * evaptotal[i]
            di[i] = 0.0 if St[i] <= Smin else kg * (St[i] - Smin)
            Pefect[i] = raintotal[j, i] - etr[i] - di[i]
            

            # **** Atualiza a coluna de agua ****
            Ct[i] = Ct[i] + Pefect[i]
            # Added by Rong
            if Ct[i] > Cmax: 
                Ct[i] = Cmax

            # **** Calcula o armazenamento e o escoamento direto ****
            if raintotal[j, i] == 0.:
                St2 = St[i] + Pefect[i]
                if Ct[i] > Cmax: St2 = Smax
            else:
                St2 = Cmin + (Smax - Cmin) * (1. - ((Cmax - Ct[i]) / (Cmax - Cmin)) ** (b + 1.))


            # **** Calcula o escoamento direto ****
            if raintotal[j, i] == 0. or Ct[i] < Cmin or (Pefect[i] - (St2 - St[i])) < 0.:
                V[i] = 0.
            else:
                V[i] = Pefect[i] - (St2 - St[i])
            Stini = St2


            # **** Calcula o fluxo base ****
            # *** para opção CUBICA
            Sgt[i] = Sgini
            Sg2 = Sgt[i] - (1 / (3 * kb * (Sgt[i]) ** 2.)) * (np.exp(-3 * kb * (Sgt[i]) ** 2. * deltat) - 1) * (di[i] - kb * (Sgt[i]) ** 3.)
            Qb[i] = kb * (Sg2 ** 3.)
            Sgini = Sg2

            # **** tranporte hidrologico ****
            if i >= 2:
                qt[i] = w0 * V[i] + w1 * V[i - 1] - delta1 * qt[i - 1] - delta2 * qt[i - 2]


            # **** Calcula o fluxo de base - BFI ****
            if N == 7:
                BFIQbi[2] = qt[3]
                if i >= 3:
                    BFIQbi[i] = (((1 - BFImax) * BFIa * BFIQbi[i - 1]) + ((1 - BFIa) * BFImax * qt[i])) / (1 - (BFImax * BFIa))
                    if BFIQbi[i] > qt[i]: BFIQbi[i] = qt[i]

            Qtotal[i] = Qb[i] + qt[i]
            Stotal[i] = St[i] + Sgt[i]

            # para aplicar a correcao com a media dos ultimos 'n' dias
            # DATA ASSIMILATION
            if (FlagMohor > 0) and (i == (numdad - 3)):
                numdiascorrege = 1
                mediacorrege = 0.0
                for contdiascorrege in range(numdiascorrege):
                    correge = (QNat_past[i - contdiascorrege]) / (Qtotal[i - contdiascorrege] * fator)
                    mediacorrege = correge / numdiascorrege + mediacorrege

                if abs(1 - mediacorrege) > abs(1 - corregeAnterior):
                    FlagMohor = 0
                    mediacorrege = 1.0
                    Sgini = Sgt[i - 1]
                    Stini = St[i - 1]
                else:
                    if abs(1 - mediacorrege) > 0.01:
                        Sgini = Sgini * mediacorrege
                        corregeAnterior = mediacorrege
                        FlagMohor = FlagMohor - 1

        # ======================================================================
        # FIM DO LOOP DIÁRIO i
        # ======================================================================
        ETRcenarios[j, :] = etr[:]
        Qcenarios[j, :] = Qtotal[:]
        Qbasecen[j, :] = Qb[:]
        Qsuperfcen[j, :] = qt[:]
        Scenarios[j, :] = Stotal[:]

    # ==========================================================================
    # FIM DO LOOP DE CENÁRIOS J
    # ==========================================================================
    
    # QgisRong: 51576094399.757
    Qtbasecen = Qbasecen * fator
    Qtsuperfcen = Qsuperfcen * fator
    Qtcenarios = Qcenarios * fator

    BFIQbiFATOR = np.zeros(numdad3)
    BFIQbiFATOR[:] = BFIQbi[:] * fator
    
    # *****estatistica total*****
    if (ESTATISTICAS == 1) and (N == 31):

        numdadESTAT = numdad - INICIOEST - 2 + 1

        RMSE = np.sqrt((np.sum((QNat_past[INICIOEST:] - Qtcenarios[4, INICIOEST:numdad]) ** 2) / numdadESTAT))  # Corrected by Rong
        DESVIO = np.sum(Qtcenarios[4, INICIOEST:numdad]) / np.sum(QNat_past[INICIOEST:])                      # Correct (Rong)
        FINVER = (1. / numdadESTAT) * np.sum(((1. / QNat_past[INICIOEST:]) - (1. / Qtcenarios[4, INICIOEST:numdad])) ** 2.) #Corrected by Rong
        ERROV = (np.sum(Qtcenarios[4, INICIOEST:numdad]) - np.sum(QNat_past[INICIOEST:])) / np.sum(QNat_past[INICIOEST:]) # Correct (Rong)

        pbias = 0.0
        sqxc, sqobs2, sqcal2, LOGQNatobs = 0., 0., 0., 0.
        xmobs, xlogs, sqdes, somq, sqlog, solog = 0., 0., 0., 0., 0., 0.
        nash, nashl = 0., 0.
        rquadradoA, rquadradoB, rquadradoC, rquadradoD, rquadradoFINAL = 0., 0., 0., 0., 0.

        for idx_s in range(INICIOEST, numdad):
            pbias = pbias + (QNat_past[idx_s] - Qtcenarios[4, idx_s])
            sqxc = sqxc + Qtcenarios[4, idx_s] * QNat_past[idx_s]
            sqobs2 = sqobs2 + QNat_past[idx_s] ** 2
            sqcal2 = sqcal2 + Qtcenarios[4, idx_s] ** 2
            LOGQNatobs = LOGQNatobs + np.log10(QNat_past[idx_s] + 0.0001)

        xmobs = np.sum(QNat_past[INICIOEST:]) / numdadESTAT
        xlogs = LOGQNatobs / numdadESTAT

        for idx_s in range(INICIOEST, numdad):
            sqdes = sqdes + (QNat_past[idx_s] - Qtcenarios[4, idx_s]) ** 2
            somq = somq + (QNat_past[idx_s] - xmobs) ** 2
            sqlog = sqlog + (np.log10(QNat_past[idx_s] + 0.0001) - np.log10(Qtcenarios[4, idx_s] + 0.0001)) ** 2
            solog = solog + (np.log10(QNat_past[idx_s] + 0.0001) - xlogs) ** 2

        nash = 1 - sqdes / somq  # Correct (Rong)
        nashl = 1 - sqlog / solog  # Correct (Rong)
        rquadradoA = (numdadESTAT * sqxc) - (np.sum(QNat_past[INICIOEST:]) * np.sum(Qtcenarios[4, INICIOEST:numdad]))
        rquadradoB = numdadESTAT * sqcal2 - (np.sum(Qtcenarios[4, INICIOEST:numdad])) ** 2
        rquadradoC = numdadESTAT * sqobs2 - (np.sum(QNat_past[INICIOEST:])) ** 2
        rquadradoD = np.sqrt(rquadradoB * rquadradoC)
        rquadradoFINAL = (rquadradoA / rquadradoD) ** 2  # Correct (Rong)
        pbias = pbias / np.sum(QNat_past[INICIOEST:])


    #Fim das estatísticas
    #***************************

    # BALANCO ARMAZENAMENTO RESERVATÓRIO Tres Marias
    #******  DADOS DE ENTRADA  ******
    archivo1 = 'DadosObserv_SaoFrancisco_TresMarias_reservatorio.csv'
    df_reservatorio = pd.read_csv(archivo1, sep=';')
    df_reservatorio.columns = df_reservatorio.columns.str.lower().str.replace(' ', '')

    Qafluente_res = df_reservatorio['qafluente'].values.astype(float)
    QExtObs_res = df_reservatorio['qdefl+qext+qvert'].values.astype(float) 

    #********** CALCULO DO BALANCO OBSERVADO  **************************************
    areadren = areabacia3 / 1000000. #km2
    volutil = 15278.0 #hm3 - Três Marias - ONS

    volutilini = 0.2531 * volutil #25.31% do vol útil acumulado em 04 de janeiro de 2017
    iInicialdoVol = 12423.0
    Evapreser = -0.8 #alterado por Lis, necessário para elevar o patamar, nosso modelo subestima o volume

    Qafluentehm3 = (Qafluente_res * 1.00 * 60 * 60 * 24) / 1000000.
    QExtObshm3 = (QExtObs_res * 60 * 60 * 24) / 1000000.
    Evaphm3 = (Evapreser * 60 * 60 * 24) / 1000000.

    dataob_dt = pd.to_datetime(df_reservatorio.iloc[:, 0].values, format='%d/%m/%Y')
    diaob, mesob, anoob = dataob_dt.day.values, dataob_dt.month.values, dataob_dt.year.values

    voluest1 = volutilini
    volestfin = np.zeros(len(df_reservatorio))

    for idx_vol in range(len(df_reservatorio)): # FOR i=0,numdad4-2 DO BEGINa partir de 4 de janeiro
        volestfin[idx_vol] = voluest1 + Qafluentehm3[idx_vol] - QExtObshm3[idx_vol] - Evaphm3
        voluest1 = volestfin[idx_vol]

    #********** INICIO DAS LINHAS MOVIDAS A PARTIR DOS GRAFICOS **************************************
    datav = date_past[:]
    data2v = date_prev[:]
    datanova = np.concatenate([[datav[-1]], data2v])

    ndias = np.arange(1, len(date_prev) + 1)
    zero = np.zeros(len(date_prev))

    #********** FIM DAS LINHAS MOVIDAS A PARTIR DOS GRAFICOS   **************************************
    z0, z1, z2, z3, z4, z5 = 0, 0, 0, 0, 0, 0
    datasim_dt = pd.to_datetime(date_prev, format='%d/%m/%Y')
    for idx_s, dt_s in enumerate(datasim_dt):
        if dt_s.day == 1 and dt_s.month == 4 and dt_s.year == 2015: z0 = idx_s + 1
        if dt_s.day == 1 and dt_s.month == 4 and dt_s.year == 2016: z1 = idx_s + 1
        if dt_s.day == 1 and dt_s.month == 4 and dt_s.year == 2017: z2 = idx_s + 1
        if dt_s.day == 30 and dt_s.month == 9 and dt_s.year == 2016: z4 = idx_s + 1
        if dt_s.day == 1 and dt_s.month == 12 and dt_s.year == 2015: z5 = idx_s + 1
        if dt_s.day == 30 and dt_s.month == 3 and dt_s.year == 2016: z3 = idx_s + 1

    diasim, messim, anosim = datasim_dt.day.values, datasim_dt.month.values, datasim_dt.year.values

    #********** INICIO DA SIMULACAO EVOLUCAO DO ARMAZENAMENTO DO Tres Marias  **************************************
    Qaflusim = Qtcenarios[:, (numdad):]
    Qaflusimhm3 = (Qaflusim * 0.96 * 60 * 60 * 24) / 1000000.
    QExthm3 = (QExt * 60 * 60 * 24) / 1000000.

    # ==========================================================================
    # FOR k=0, 0 - LOOP DA SIMULACAO DO RESERVATÓRIO
    # ==========================================================================
    for k in range(1):
        volp75mefin = np.zeros(numdad2)
        
        volp50mefin = np.zeros(numdad2)
        volp30mefin = np.zeros(numdad2)
        volp25mefin = np.zeros(numdad2)
        volprevfin = np.zeros(numdad2)
        volp25maisfin = np.zeros(numdad2)
        volp50maisfin = np.zeros(numdad2)

        volutilini_k = voluest1
        volprev0 = volutilini_k; volprev1 = volutilini_k; volprev2 = volutilini_k; volprev3 = volutilini_k
        volprev4 = volutilini_k; volprev5 = volutilini_k; volprev6 = volutilini_k

        for idx_i in range(numdad2): # FOR i=0,numdad2-2 DO BEGIN
            volp75mefin[idx_i] = volprev0 + Qaflusimhm3[0, idx_i] - QExthm3[idx_i] - Evaphm3
            volprev0 = volp75mefin[idx_i]
            volp50mefin[idx_i] = volprev1 + Qaflusimhm3[1, idx_i] - QExthm3[idx_i] - Evaphm3
            volprev1 = volp50mefin[idx_i]
            volp30mefin[idx_i] = volprev2 + Qaflusimhm3[2, idx_i] - QExthm3[idx_i] - Evaphm3
            volprev2 = volp30mefin[idx_i]
            volp25mefin[idx_i] = volprev3 + Qaflusimhm3[3, idx_i] - QExthm3[idx_i] - Evaphm3
            volprev3 = volp25mefin[idx_i]
            volprevfin[idx_i] = volprev4 + Qaflusimhm3[4, idx_i] - QExthm3[idx_i] - Evaphm3
            volprev4 = volprevfin[idx_i]
            volp25maisfin[idx_i] = volprev5 + Qaflusimhm3[5, idx_i] - QExthm3[idx_i] - Evaphm3
            volprev5 = volp25maisfin[idx_i]
            volp50maisfin[idx_i] = volprev6 + Qaflusimhm3[6, idx_i] - QExthm3[idx_i] - Evaphm3
            volprev6 = volp50maisfin[idx_i]

        # INICIO GRAFICA SERIES 
        if (PLOTARGRAFICOS == 1) and (k == 0) and (N == 21): #<alice;karinne>
            plt.figure(figsize=(12, 6))
            x_passado = datasazo_dt[11927:(numdad)]
            x_futuro = datasazo_dt[11927:min(numdad+101, len(datasazo_dt))]
            
            plt.plot(x_passado, QNat_past[11927:], color='black', label='Q Obs.', linewidth=2.0)
            plt.plot(x_futuro, Qtcenarios[4, 11927:min(numdad+101, len(datasazo_dt))], color='red', label='Q Calc.', linewidth=2.0)
            
            plt.title('Tres Marias')
            plt.ylabel('Vazao (m3/s)')
            plt.xlabel('Dia')
            plt.legend(loc='center right')
            plt.grid(True, which='both', linestyle='--', alpha=0.5)
            
            str_ano, str_mes, str_dia = str(anoob[-1]), f"{mesob[-1]:02d}", f"{diaob[-1]:02d}"
            plt.savefig(f'TM_ObsxSim_zoom_{str_ano}_{str_mes}_{str_dia}_NOVO.jpg', dpi=200, bbox_inches='tight')
            plt.show()

        # FIM GRAFICA SERIES

        
        if (k == 0) and (N == 21): 
            str_ano, str_mes, str_dia = str(anoob[-1]), f"{mesob[-1]:02d}", f"{diaob[-1]:02d}"
            
            with open(f'TM_Q_ResulCalib_{str_ano}_{str_mes}_{str_dia}_NOVO.txt', 'w') as f35:
                f35.write('        Data      Qtotal        Qsup       Qbase         ETR           S Qbasefiltro\n')
                for idx_out in range(numdad):
                    f35.write(f"{date_past[idx_out]:12}{Qtcenarios[4, idx_out]:12.2f}{Qtsuperfcen[4, idx_out]:12.2f}{Qtbasecen[4, idx_out]:12.2f}{ETRcenarios[4, idx_out]:12.2f}{Scenarios[4, idx_out]:12.2f}{BFIQbiFATOR[idx_out]:12.2f}\n")

            with open(f'TM_V_Sim_{str_ano}_{str_mes}_{str_dia}_NOVO.txt', 'w') as f50:
                for idx_out in range(numdad2):
                    f50.write(f"{ndias[idx_out]:5}{datanova[idx_out]:16}{volp75mefin[idx_out]:12.3f}{volp50mefin[idx_out]:12.3f}{volp30mefin[idx_out]:12.3f}{volp25mefin[idx_out]:12.3f}{volprevfin[idx_out]:12.3f}{volp25maisfin[idx_out]:12.3f}{volp50maisfin[idx_out]:12.3f}\n")

            with open(f'TM_V_Sim_Passado_{str_ano}_{str_mes}_{str_dia}_NOVO.csv', 'w') as f20:
                for idx_out in range(len(df_reservatorio)):
                    f20.write(f"{df_reservatorio.iloc[idx_out, 0]},{volestfin[idx_out]:12.3f}\n")

        #////////////INICIO DAS SAIDAS COM AS VAZOES PREVISTAS E PROJETADAS\\\\\\\\\\\\
        if k == 0:
            str_ano, str_mes, str_dia = str(anoob[-1]), f"{mesob[-1]:02d}", f"{diaob[-1]:02d}"
            for idx_f in range(diasPrevisaoChuva):
                QFUTURAS[N, idx_f] = Qtcenarios[4, numdad + idx_f]

            if N == 31:
                with open(f'TM_QNat_Cenarios_{str_ano}_{str_mes}_{str_dia}_NOVO.txt', 'w') as f40:
                    for idx_out in range(numdad2):
                        str_qt = "".join([f"{val:8.2f}" for val in Qtcenarios[:, numdad + idx_out]])
                        str_etr = "".join([f"{val:8.2f}" for val in ETRcenarios[:, numdad + idx_out]])
                        str_scen = "".join([f"{val:10.2f}" for val in Scenarios[:, numdad + idx_out]])
                        f40.write(f"{date_prev[idx_out]:12}{str_qt}{str_etr}{str_scen}\n")

            if N == 32: #Saida Q cenário P1963
                with open(f'TM_QNat_Pcritica_{str_ano}_{str_mes}_{str_dia}_NOVO.csv', 'w') as f37:
                    for idx_out in range(numdad2):
                        f37.write(f"{date_prev[idx_out]};{Qtcenarios[4, numdad + idx_out]:.2f}\n")
                with open(f'TM_V_Sim_Pcritica_{str_ano}_{str_mes}_{str_dia}_NOVO.csv', 'w') as f43:
                    for idx_out in range(numdad2):
                        f43.write(f"{ndias[idx_out]},{datanova[idx_out]},{volprevfin[idx_out]:.3f}\n")

            if N == 33: #Saida Q cenário Pcrítico
                with open(f'TM_QNat_P_minima_mensal_{str_ano}_{str_mes}_{str_dia}_NOVO.csv', 'w') as f17:
                    for idx_out in range(numdad2):
                        f17.write(f"{date_prev[idx_out]};{Qtcenarios[4, numdad + idx_out]:.2f}\n")
                with open(f'TM_V_Sim_P_minima_mensal_{str_ano}_{str_mes}_{str_dia}_NOVO.csv', 'w') as f50_c:
                    for idx_out in range(numdad2):
                        f50_c.write(f"{ndias[idx_out]},{datanova[idx_out]},{volprevfin[idx_out]:.3f}\n")
    
    # ==========================================================================
    # FIM DO LOOP DA SIMULACAO DO RESERVATÓRIO
    # ==========================================================================

# ==============================================================================
# FIM DO LOOP DOS MEMBROS DE PRECIPITACAO
# ==============================================================================

print()
print('MES       Q obs mensal       Q sim mensal')

# ;PRINT,'07/2016',MEAN(QNat_past(12235:12265)),MEAN(Qtcenarios(4,12235:12265))

# No IDL: mesob(0,numdad4-2) acessa o mês da última linha válida. 
# Em Python, pegamos o último elemento do vetor 'mesob' usando o índice [-1].
mes_final = f"{mesob[-1]:02d}"

# Cálculo das médias mensais usando np.mean do NumPy
# Ajustamos os fatiamentos de índices para a sintaxe exclusiva do Python
inicio_recorte = numdad - diaob[-1]
q_obs_mensal = np.mean(QNat_past[inicio_recorte:])
q_sim_mensal = np.mean(Qtcenarios[4, inicio_recorte : numdad])

print(f"{mes_final}         {q_obs_mensal:.2f}            {q_sim_mensal:.2f}")

# Exibe o Pbias final calculado em porcentagem
print(f"Pbias = {pbias * 100:.2f} %")

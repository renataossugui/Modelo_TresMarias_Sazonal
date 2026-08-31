import os
import zipfile
import numpy as np
import pandas as pd

# 1. Configurações de pastas
pasta_zips = r"C:\Users\yurio\Downloads\dados_uhe_caconde\INMET"  
pasta_saida = r"C:\Users\yurio\Downloads\dados_uhe_caconde\INMET\dados_inmet_tratados"
os.makedirs(pasta_saida, exist_ok=True)

# 2. Estações de interesse
estacoes = [
    "INMET_SE_SP_A738_CASA BRANCA",
    "INMET_SE_MG_A567_MACHADO",
    "INMET_SE_MG_A530_CALDAS"
]

# Nomes padronizados para todas as 19 colunas do INMET
colunas_padrao = [
    'Data',
    'Hora UTC',
    'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)',
    'PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)',
    'PRESSAO ATMOSFERICA MAX. NA HORA ANT. (AUT) (mB)',
    'PRESSAO ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)',
    'RADIACAO GLOBAL (Kj/m²)',
    'TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)',
    'TEMPERATURA DO PONTO DE ORVALHO (°C)',
    'TEMPERATURA MÁXIMA NA HORA ANT. (AUT) (°C)',
    'TEMPERATURA MÍNIMA NA HORA ANT. (AUT) (°C)',
    'TEMPERATURA ORVALHO MAX. NA HORA ANT. (AUT) (°C)',
    'TEMPERATURA ORVALHO MIN. NA HORA ANT. (AUT) (°C)',
    'UMIDADE REL. MAX. NA HORA ANT. (AUT) (%)',
    'UMIDADE REL. MIN. NA HORA ANT. (AUT) (%)',
    'UMIDADE RELATIVA DO AR, HORARIA (%)',
    'VENTO, DIREÇÃO HORARIA (gr) (° (gr))',
    'VENTO, RAJADA MAXIMA (m/s)',
    'VENTO, VELOCIDADE HORARIA (m/s)'
]

dados = {est: [] for est in estacoes}

# 3. Leitura direta dos arquivos ZIP
for nome_zip in [f for f in os.listdir(pasta_zips) if f.endswith('.zip')]:
    with zipfile.ZipFile(os.path.join(pasta_zips, nome_zip), 'r') as z:
        for arq in z.namelist():
            for est in estacoes:
                if est in arq and arq.upper().endswith('.CSV'):
                    with z.open(arq) as f:
                        try:
                            df = pd.read_csv(
                                f, 
                                skiprows=8, 
                                sep=';', 
                                encoding='latin-1', 
                                decimal=',',
                                na_values=['-9999', -9999, '-9999.0', -9999.0]
                            )
                        except UnicodeDecodeError:
                            f.seek(0)
                            df = pd.read_csv(
                                f, 
                                skiprows=8, 
                                sep=';', 
                                encoding='utf-8', 
                                decimal=',',
                                na_values=['-9999', -9999, '-9999.0', -9999.0]
                            )

                        # Mantém as 19 colunas de dados
                        df = df.iloc[:, :19]
                        df.columns = colunas_padrao[:df.shape[1]]
                        
                        # Converte colunas de medição para numérico real (float)
                        for col in df.columns[2:]:
                            if df[col].dtype == 'object':
                                df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                        
                        # Substitui qualquer resíduo de -9999 por vazio (NaN)
                        df = df.replace([-9999, -9999.0, '-9999', '-9999.0'], np.nan)
                        
                        dados[est].append(df)

# 4. Concatena e salva em formato Excel (.xlsx) com células vazias
print("\n--- Salvando arquivos consolidados em Excel ---")
for est, lista_df in dados.items():
    if lista_df:
        df_final = pd.concat(lista_df, ignore_index=True).dropna(how='all')
        
        # Garante que todos os -9999 fiquem vazios no Excel final
        df_final = df_final.replace([-9999, -9999.0], np.nan)
        
        caminho_xlsx = os.path.join(pasta_saida, f"{est.replace(' ', '_')}_completo.xlsx")
        
        # Salva no Excel (valores NaN são gravados automaticamente como células vazias)
        df_final.to_excel(caminho_xlsx, index=False, engine='openpyxl')
        print(f"Salvo: {caminho_xlsx} ({len(df_final)} registros | {len(df_final.columns)} colunas)")
    else:
        print(f"Aviso: Nenhum dado encontrado para {est}.")
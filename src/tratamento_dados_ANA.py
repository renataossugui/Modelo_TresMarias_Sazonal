import os
import pandas as pd

# Lista com os nomes das pastas fornecidas
pastas = ['61812000'
] #'61802502', '61807002', '61811080',"61813000",'2146075','2146074','2146117'

# Diretorio onde as pastas estao localizadas (use '.' para a pasta atual ou coloque o caminho completo)
caminho_base = r"C:\Users\yurio\OneDrive\Documentos\SABER-PARDO\dados_uhe_caconde\dados_ANA"

# Dicionario para armazenar os DataFrames finais processados
dataframes_processados = {}

def carregar_e_formatar_excel(caminho_arquivo, tipo_medicao):
    """
    Funcao para ler a planilha e transformar o formato horizontal (dias nas colunas)
    em uma serie temporal continua (Data em linhas e Valor medido em coluna).
    """
    df = pd.read_csv(caminho_arquivo, sep=';', decimal=',')

    # Identifica as colunas que correspondem aos dias (ex: Chuva01, Vazao01, etc.)
    colunas_dias = [col for col in df.columns if col.startswith(tipo_medicao)]

    # Transforma as colunas dos dias em linhas usando melt
    df_long = pd.melt(
        df,
        id_vars=['Data'], 
        value_vars=colunas_dias, 
        var_name='Dia_Str', 
        value_name=tipo_medicao
    )
    
    # Extrai apenas o numero do dia a partir do nome da coluna (ex: 'Chuva01' -> '01')
    df_long['Dia'] = df_long['Dia_Str'].str.extract(r'(\d+)').astype(int)
    
    # Formato explícito: %d (dia), %m (mês), %Y (ano de 4 dígitos)
    df_long['Data_Mes'] = pd.to_datetime(df_long['Data'], format='%d/%m/%Y', errors='coerce')
    df_long['Ano'] = df_long['Data_Mes'].dt.year
    df_long['Mes'] = df_long['Data_Mes'].dt.month

    # Cria a data exata combinando Ano, Mes e Dia (descarta dias invalidos como 31 de fev)
    df_long['Data_Final'] = pd.to_datetime(
        df_long[['Ano', 'Mes', 'Dia']].rename(columns={'Ano': 'year', 'Mes': 'month', 'Dia': 'day'}),
        errors='coerce'
    )
    
    # Remove datas invalidas resultantes da conversao
    df_long = df_long.dropna(subset=['Data_Final'])
    df_long['Data_Final'] = df_long['Data_Final'].dt.strftime("%d/%m/%Y")
    # Ordena os dados cronologicamente
    df_final = df_long[['Data_Final', tipo_medicao]].sort_values('Data_Final').reset_index(drop=True)

    return df_final


# Processing loop
for pasta in pastas:
    caminho_pasta = os.path.join(caminho_base, pasta)

    # Procura por arquivos dentro da pasta
    arquivos_na_pasta = os.listdir(caminho_pasta)
    
    for arquivo in arquivos_na_pasta:
        if arquivo.endswith('.csv'):
            caminho_completo = os.path.join(caminho_pasta, arquivo)
            
            # Identifica se é do tipo Chuva ou Vazao
            if "_Chuva" in arquivo or "PLUVIOMETRO" in pasta:
                tipo = "Chuva"
            elif "_Vazoes" in arquivo or "FLUVIOMETRO" in pasta:
                tipo = "Vazao"
            else:
                continue  
            
            print(f"Processando: {arquivo} (Tipo: {tipo})...")

            # Processa o dataframe
            df_resultado = carregar_e_formatar_excel(caminho_completo, tipo)

            # Armazena no dicionario com a chave do nome da pasta / estacao
            chave = f"{pasta}_{tipo}"
            dataframes_processados[chave] = df_resultado

            pasta_codigo = arquivo.split('_')[0]
            
            # Define o nome do arquivo final Excel
            caminho_Excel = os.path.join(caminho_base, pasta_codigo, f"{pasta_codigo}_tratado.xlsx")
            
            # Salva em Excel com codificação UTF-8 e sem o índice numérico
            df_resultado.to_excel(caminho_Excel)
            print(f"Salvo com sucesso: {caminho_Excel}")
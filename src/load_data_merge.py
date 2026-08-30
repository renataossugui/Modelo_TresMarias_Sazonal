import os
import urllib.request
from datetime import datetime, timedelta
import pandas as pd
import rasterio

# --- CONFIGURAÇÕES ---
data_inicio = datetime(2010, 1, 1)
data_fim = datetime(2026, 8, 15)
lat_alvo = -21.5333
lon_alvo = -46.6333

saida_csv = r"c:\saber-pardo\modelo_tresmarias_sazonal\src\serie_merge_precipitacao_GPM_2010_2026_2146007.csv"

# --- LOOP DE EXTRAÇÃO ---
resultados = []
data_atual = data_inicio

while data_atual <= data_fim:
    ano = data_atual.strftime("%Y")
    mes = data_atual.strftime("%m")
    dia_str = data_atual.strftime("%Y%m%d")

    url = f"https://ftp.cptec.inpe.br/modelos/tempo/MERGE/GPM/DAILY/{ano}/{mes}/MERGE_CPTEC_{dia_str}.grib2"
    temp_grib = f"temp_{dia_str}.grib2"

    try:
        urllib.request.urlretrieve(url, temp_grib)

        with rasterio.open(temp_grib) as src:
            # Extrai os dados da Banda 1 (Precipitação em mm) no ponto (lon, lat)
            # Obs: o sample espera a tupla (x, y) -> (longitude, latitude)
            coords = [(lon_alvo, lat_alvo)]
            valores = [val[0] for val in src.sample(coords, indexes=1)]
            valor_raw = float(valores[0])

            # Tratamento de NoData / Valores ausentes
            if (
                valor_raw < 0
                or valor_raw > 1000
                or pd.isna(valor_raw)
                or valor_raw == 9999.0
            ):
                valor_prec = 0.0
            else:
                valor_prec = valor_raw

            resultados.append(
                {
                    "data": data_atual.strftime("%Y-%m-%d"),
                    "precipitacao_mm": round(valor_prec, 2),
                }
            )
            print(f"{dia_str}: {round(valor_prec, 2)} mm")

    except Exception as e:
        print(f"Erro ou dado indisponível em {dia_str}: {e}")

    finally:
        if os.path.exists(temp_grib):
            os.remove(temp_grib)

    data_atual += timedelta(days=1)

# --- SALVAR TABELA ---
df = pd.DataFrame(resultados)
df.to_csv(saida_csv, index=False)
print("\n--> SUCESSO! Série de precipitação salva em:", saida_csv)
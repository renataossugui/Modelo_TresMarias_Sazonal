import os
import urllib.request
from datetime import datetime, timedelta
import pandas as pd
import xarray as xr

# 1. Configurações
data_inicio = datetime(2023, 1, 1)   # Ajuste a data inicial
data_fim = datetime(2025, 12, 31)     # Ajuste a data final
lat_alvo = -21.47085
lon_alvo = -46.53297
saida_csv = r"G:/Meu Drive/dados_uhe_caconde/dados_samet/serie_samet_ponto_estacao_TMED_CIIAGRO.csv"

# 2. Loop pelas datas online
resultados = []
data_atual = data_inicio

while data_atual <= data_fim:
    ano = data_atual.strftime("%Y")
    mes = data_atual.strftime("%m")
    dia_str = data_atual.strftime("%Y%m%d")
    
    url = f"https://ftp.cptec.inpe.br/modelos/tempo/SAMeT/DAILY/TMED/{ano}/{mes}/SAMeT_CPTEC_TMED_{dia_str}.nc"
    temp_nc = "temp.nc"

    try:
        urllib.request.urlretrieve(url, temp_nc)
        with xr.open_dataset(temp_nc) as ds:
            # Identifica os nomes das coordenadas de latitude e longitude
            lat_k = 'lat' if 'lat' in ds.coords else 'latitude'
            lon_k = 'lon' if 'lon' in ds.coords else 'longitude'
            
            ponto = ds.sel({lat_k: lat_alvo, lon_k: lon_alvo}, method="nearest")
            var_name = list(ds.data_vars)[0]
            valor_temp = float(ponto["tmed"].values.item())
            
            resultados.append({"data": data_atual.strftime("%Y-%m-%d"), "temperatura_TMED_C": round(valor_temp, 2)})
            print(f"{dia_str}: {round(valor_temp, 2)} °C")
            
        os.remove(temp_nc)
    except Exception:
        print(f"Dado indisponível para: {dia_str}")
        
    data_atual += timedelta(days=1)

# 3. Salva a tabela final
df = pd.DataFrame(resultados)
df.to_csv(saida_csv, index=False)
print("Tabela gerada com sucesso em:", saida_csv)
# 🌧️ Modelo Hidrológico PDM - Bacia do Reservatório de Três Marias

Este repositório contém a implementação em Python do **Probability-Distributed Model (PDM)** adaptado pelo **CEMADEN** (Centro Nacional de Monitoramento e Alertas de Desastres Naturais). O modelo realiza a simulação hidrológica chuva-vazão de escala diária e projeta a evolução do armazenamento no reservatório da Usina Hidrelétrica de Três Marias (Bacia do Rio São Francisco).

* **Autora:** Adriana Cuartas (`adriana.cuartas@cemaden.gov.br`)
* **Desenvolvimento e Modificações:** Eduardo Luz, Luiz Valério de Castro Carvalho, Rong Zhang
* **Instituição:** CEMADEN - Centro Nacional de Monitoramento e Alertas de Desastres Naturais

---

## 📌 Visão Geral do Modelo

O script integra:

1. **Simulação Hidrológica Concentrada (PDM):** Transforma dados diários de chuva e evapotranspiração potencial em vazão natural no exutório da bacia.

2. **Calibração Sazonal Dinâmica:** Aplica parâmetros diferenciados para as estações **Chuvosa (WET)**, **Seca (DRY)** e **Transição (TST)** com base no mês do ano.

3. **Assimilação de Dados (*State Update*):** Reajusta os reservatórios internos de umidade do solo (S_t e Ssgt) utilizando a vazão observada recente antes de iniciar as projeções futuras.

4. **Previsão por Ensemble e Cenários:** Simula vazões e balanço de volume útil para 31 membros de previsão numérica de tempo (GEFS/ETA) combinados a 7 cenários de variação percentual de precipitação (de -75\% a +50\%) e cenários de secas históricas severas.



---

## 📂 Estrutura de Arquivos de Entrada

Para a execução correta, o script exige três arquivos CSV formatados com delimitador `;`:

### 1. `PEQ_SaoFrancisco_TresMarias_passado.csv`

Contém as forçantes históricas e monitoradas da bacia:

* `dia`: Data do registro (`DD/MM/AAAA`).
* `prec(mm)`: Precipitação diária observada acumulada (mm/dia).
* `evapora_hs2003`: Evapotranspiração potencial estimada pelo método Hargreaves-Samani (mm/dia).
* `qnat`: Vazão natural observada no rio (m³/s).



### 2. `PE_SaoFrancisco_TresMarias_futuro.csv`

Contém as projeções de chuva, evapotranspiração e demandas operacionais:

* `data`: Data da previsão/projeção (`DD/MM/AAAA`).
* Colunas de 1 a 31 (`membro1` a `membro31`): Precipitação diária prevista pelos membros do ensemble (mm/dia).
* `etp`: Evapotranspiração potencial prevista (mm/dia).
* `qdefluencia(ons+2025)+qvert`: Vazão defluente turbinada + vertida planejada (m³/s).
* `qext`: Retiradas e captações de água diretas (m³/s).
* `pcritico_mar-set2021+anocritico2014`: Série sintética de chuva para cenário de seca crítica.
* `cenarioprecminimamensal`: Série sintética de chuva com mínimos históricos mensais.



### 3. `DadosObserv_SaoFrancisco_TresMarias_reservatorio.csv`

Contém os dados operacionais da barragem de Três Marias:

* `qafluente`: Vazão afluente observada que entra no reservatório (m³/s).
* `qdefl+qext+qvert`: Vazão total de saída observada (m³/s).



---

## ⚙️ Parâmetros de Calibração Sazonal

Os parâmetros do PDM variam dinamicamente conforme o índice sazonal da data:

| Parâmetro | Descrição | Estação Chuvosa (WET) | Estação Seca (DRY) |
| --- | --- | --- | --- |
| Cmax | Cap. máx. de armazenamento do solo (mm) | 1.504,7<br> | 947,9<br> |
| Cmin | Cap. mín. de armazenamento do solo (mm) | 156,5<br> | 92,2<br> |
| b | Expoente da distribuição de Pareto | 0,420<br> | 0,191<br> |
| k_g | Inverso da constante de recarga subterrânea | 638,47<br> | 709,19<br> |
| k_b | Inverso da constante do fluxo de base | 3.061,5<br> | 3.076,5<br> |
| k_1 | Constante do 1º reservatório superficial | 2,00<br> | 4,37<br> |
| k_2 | Constante do 2º reservatório superficial | 5,49<br> | 8,84<br> |

---

## 📊 Arquivos Gerados (Outputs)

Ao final da execução, o script gera automaticamente na pasta de trabalho:

### Relatórios em Texto/Tabelas (`.txt` e `.csv`)

* **`TM_Q_ResulCalibsDATA}.txt`:** Série histórica do passado simulado contendo vazão total, escoamento superficial, fluxo de base, evapotranspiração real e umidade do solo.
* **`TM_V_SimsDATA}.txt`:** Projeção diária do volume útil do reservatório (hm³) para os 7 cenários de variação de chuva.
* **`TM_V_Sim_PassadosDATA.csv`:** Balanço do volume útil acumulado calculado para o período histórico.
* **`TM_QNat_CenariossDATA.txt`:** Projeção das vazões diárias para todos os cenários futuros de chuva.
* **`TM_QNat_PcriticasDATA.csv` / `TM_V_Sim_PcriticasDATA.csv`:** Vazão e volume projetados sob o cenário de seca crítica de longo prazo.
* **`TM_QNat_P_minima_mensalsDATA}.csv` / `TM_V_Sim_P_minima_mensalsDATA.csv`:** Vazão e volume projetados para o cenário de chuva mínima mensal histórica.



### Gráficos

* **`TM_ObsxSim_zoomsDATA}_NOVO.jpg`:** Gráfico comparativo entre a vazão natural observada e a vazão calculada pelo modelo PDM no período recente e de previsão.


---

##  Como Executar

### Pré-requisitos

Certifique-se de ter o Python 3.x instalado acompanhado das seguintes bibliotecas:

```bash
pip install numpy pandas matplotlib

```

### Configuração e Execução

1. Abra o arquivo do script e ajuste a variável `PATH` com o caminho local onde os arquivos CSV estão armazenados:
```python
PATH = r'SEU_CAMINHO_LOCAL/Modelo_TresMarias_Sazonal/scr/'

```

2. Execute o script principal:
```bash
python Modelo_TresMarias_Sazonal.py

```

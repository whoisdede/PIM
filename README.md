# 1. Objetivo da análise

O objetivo é comparar os seis métodos utilizados, disponíveis no OpenCV cv.match Template - TM_SQDIFF, TM_SQDIFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_CCOEFF, TM_CCOEFF_NORMED - aplicando nos 300 frames, com base nas curvas do .csv e dos gráficos.

Critérios usados na comparação:
* **Estabilidade:** Será analisado a estabilidade da curva do valor bom de casamento, que é o valor que o algoritmo usa para localizar o objeto max_val para os métodos de correlação e min_val para os de diferença quadrada, medida pelo coeficiente de variação ($CV=$ desvio padrão / média);
* **Discriminação:** entre o valor de melhor casamento e o de pior casamento em cada quadro;
* **Sensibilidade:** método para mudanças na cena, como o objeto se desloca, saindo do quadro.
* **Normalização:** uma faixa de valores fixa, facilitando a definição de limiares (theresholds) automáticos de aceitação/rejeição do casamento.

### estatustica geral

| Método | Métrica usada | Média | Desvio padrão | CV (%) | Faixa de valores |
| :--- | :--- | :--- | :--- | :--- | :--- |
| TM_CCOEFF | max_val | $5,26\times10^{7}$ | $3,15\times10^{6}$ | 6,0 | não normalizado |
| TM_CCOEFF_NORMED | max_val | 0,861 | 0,064 | 7,5 | [-1, 1] |
| TM_CCORR | max_val | $2,97\times10^{8}$ | $5,72\times10^{6}$ | 1,9 | não normalizado |
| TM_CCORR_NORMED | max_val | 0,949 | 0,026 | 2,7 | [0, 1] |
| TM_SQDIFF | min_val | $1.89\times10^{7}$ | $1.14\times10^{7}$ | 60,0 | não normalizado |
| TM_SQDIFF_NORMED | min_val | 0,118 | 0,068 | 58,2 | [0, 1] |

---

# 2. Analisando cada método

### • TM_SQDIFF e TM SQDIFF_NORMED
Apresentam o maior coeficiente de variação (≈ 60%), evidenciado nos gráficos pela curva azul min_val bastante irregular. Isso mostra alta sensibilidade a qualquer mudança na cena, mas também maior ruído, o método não faz nenhuma normalização por brilho/contraste, então variações de iluminação entre quadros afetam diretamente o valor da diferença quadrada. Além disso, a busca é por mínimo, e trabalhar com "quanto menor, melhor" exige inverter a lógica de decisão do rastreador, o que é um pouco menos intuitivo. A versão _NORMED reduz a escala para [0,1], mas mantém o mesmo padrão de ruído relativo.

### • TM_CCORR E TM_CCORR_NROMED
Têm a menor variação relativa entre todos os métodos ($(CV\approx2-3\%)$), mas o seu principal problema: TM_CCOR não subtrai a média (não é mean-removed) nem compensa a energia da imagem, por isso o valor de correlação é fortemente dominado pelo brilho e pela energia geral do quadro, e não apenas pela real semelhança de forma com o template. Na prática, a curva fica "achatada" mesmo quando o objeto se move, porque regiões claras e uniformes do fundo tendem a gerar correlação alta mesmo sem casamento genuíno. Isso é visível nos gráficos: TM_CCORR e TM_CCORR_NORMED têm curvas de max_val mais suaves/planas que TM_CCOEFF_NORMED, refletindo baixa discriminação entre "template no lugar certo" e "template em outro lugar parecido em brilho".

### • TM_CCOEFF e TM_CCOEFF_NORMED
Esses métodos subtraem a média do template e da região da imagem antes de calcular a correlação (são versões mean-removed da correlação cruzada), o que os torna, teoricamente, os mais robustos a variações de iluminação e brilho de fundo. A versão TM_CCOEFF_NORMED corresponde, matematicamente, ao coeficiente de correlação de Pearson entre o template e a região comparada, sendo normalizada para o intervalo [-1, 1], que facilita a definição de um limiar fixo de aceitação (ex.: só considerar válido um casamento com max_val > 0,8). Nos dados, seu max_val tem CV moderado (7,5%) sem ficar "achatado" como o do TM_CCORR, indicando que reage às mudanças reais da cena sem ser dominado pelo brilho absoluto.

---

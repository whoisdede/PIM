import cv2
import numpy as np
import matplotlib.pyplot as plt
import csv
import os
import glob

# Diretórios de entrada e saída
input_dir = "/home/andre/main/PIM/PIM"
output_dir = "/home/andre/main/PIM/output"

# Cria diretório de saída se não existir
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Carrega todas as imagens .bmp do diretório em ordem
image_paths = sorted(glob.glob(os.path.join(input_dir, "*.bmp")))
if not image_paths:
    print("Nenhuma imagem .bmp encontrada no diretório especificado.")
    exit()

# Passo D: Seleção do template na primeira imagem (im1)
# Lê a primeira imagem e converte para tons de cinza
img1_color = cv2.imread(image_paths[0])
img1_gray = cv2.cvtColor(img1_color, cv2.COLOR_BGR2GRAY)

# Permite que você selecione a Região de Interesse (ROI) com o mouse
print("Selecione o objeto a ser rastreado e pressione ENTER ou ESPAÇO.")
roi = cv2.selectROI("Selecione o Template", img1_color, showCrosshair=True, fromCenter=False)
cv2.destroyWindow("Selecione o Template")

# Recorta o template da imagem em tons de cinza
x, y, w, h = int(roi[0]), int(roi[1]), int(roi[2]), int(roi[3])
template = img1_gray[y:y+h, x:x+w]

# Métodos exigidos pela tarefa
methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR', 
           'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']

# Dicionário para armazenar os resultados (min_val e max_val) de cada método
results = {meth: {'frames': [], 'min_vals': [], 'max_vals': [], 'best_locs': []} for meth in methods}

# Passo E: Aplicar cvMatchTemplate para cada quadro com todos os métodos
print("Processando imagens...")
for frame_idx, img_path in enumerate(image_paths): # Começa do im1 (índice 0) até o final
    # Lê a imagem em tons de cinza
    img_gray = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    frame_number = frame_idx + 1 # Para nomear como im1, im2, im3...
    
    for meth_name in methods:
        method = eval(meth_name)
        
        # Aplica o Template Matching
        res = cv2.matchTemplate(img_gray, template, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        # Armazena os valores
        results[meth_name]['frames'].append(frame_number)
        results[meth_name]['min_vals'].append(min_val)
        results[meth_name]['max_vals'].append(max_val)
        
        # Para SQDIFF, o melhor match é o valor mínimo. Para os outros, é o máximo.
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            results[meth_name]['best_locs'].append(min_loc)
        else:
            results[meth_name]['best_locs'].append(max_loc)

# Passo E (Continuação): Salvar os resultados em arquivos CSV
for meth_name in methods:
    csv_filename = os.path.join(output_dir, f"{meth_name.replace('cv2.', '')}.csv")
    with open(csv_filename, mode='w', newline='') as file:
        writer = cv2.csv.writer(file) if hasattr(cv2, 'csv') else csv.writer(file)
        # Cabeçalho exigido
        writer.writerow(['Método', 'Quadro (imagem)', 'min_val', 'max_val'])
        
        frames = results[meth_name]['frames']
        min_vals = results[meth_name]['min_vals']
        max_vals = results[meth_name]['max_vals']
        
        for i in range(len(frames)):
            # Pula a im1 no CSV se desejar, mas registrar todos ajuda na plotagem
            writer.writerow([meth_name.replace('cv2.', ''), f'im{frames[i]}', min_vals[i], max_vals[i]])
            
    print(f"CSV salvo: {csv_filename}")

# Passo F: Gerar os gráficos para cada método 8
for meth_name in methods:
    plt.figure(figsize=(10, 5))
    plt.plot(results[meth_name]['frames'], results[meth_name]['min_vals'], label='min_val', color='blue')
    plt.plot(results[meth_name]['frames'], results[meth_name]['max_vals'], label='max_val', color='red')
    
    plt.title(f"Template Matching - {meth_name.replace('cv2.', '')}")
    plt.xlabel('Imagem (Quadro)')
    plt.ylabel('Valores de Match')
    plt.legend()
    plt.grid(True)
    
    plot_filename = os.path.join(output_dir, f"grafico_{meth_name.replace('cv2.', '')}.png")
    plt.savefig(plot_filename)
    plt.close()
    print(f"Gráfico salvo: {plot_filename}")

# Passo H: Gerar vídeo de saída com o melhor método
# Escolhemos TM_CCOEFF_NORMED como "melhor" por padrão (ele lida bem com iluminação média)
# Você deve justificar isso no relatório (Passo G).
best_method_name = 'cv2.TM_CCOEFF_NORMED'
print(f"Gerando vídeo de saída usando o método: {best_method_name}")

# Configura o VideoWriter do OpenCV
first_img = cv2.imread(image_paths[0])
height_img, width_img, layers = first_img.shape
# Usando o codec mp4v que tem boa compatibilidade no Ubuntu
video_writer = cv2.VideoWriter(os.path.join(output_dir, 'video_saida.mp4'), 
                               cv2.VideoWriter_fourcc(*'mp4v'), 15, (width_img, height_img))

for idx, img_path in enumerate(image_paths):
    img_color = cv2.imread(img_path)
    
    # Recupera a melhor posição encontrada para este frame
    top_left = results[best_method_name]['best_locs'][idx]
    bottom_right = (top_left[0] + w, top_left[1] + h)
    
    # Desenha o retângulo vermelho de rastreio
    cv2.rectangle(img_color, top_left, bottom_right, (0, 0, 255), 2)
    
    video_writer.write(img_color)

video_writer.release()
print("Processamento concluído. Verifique a pasta output.")
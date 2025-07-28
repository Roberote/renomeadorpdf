import os  # Módulo para manipular arquivos e diretórios
import pytesseract  # Interface Python para o Tesseract OCR
from pdf2image import convert_from_path  # Converte PDF para imagem
from PIL import Image, ImageFilter, ImageEnhance  # Manipulação de imagem
import shutil  # Para copiar e mover arquivos

# ============================
# CONFIGURAÇÕES DO SISTEMA
# ============================

# Define o caminho do executável do Tesseract OCR
# (altere este caminho se estiver diferente em outra máquina)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Define o caminho da pasta "bin" do Poppler (necessário para converter PDF em imagem)
poppler_path = r'C:\Users\Robert\Desktop\Coisax\poppler-24.08.0\Library\bin'

# Caminho da pasta onde estão os PDFs ainda não renomeados
input_folder = r'C:\Users\Robert\Desktop\renomeador\pdf'

# Caminho da pasta onde os PDFs renomeados serão salvos
output_folder = r'C:\Users\Robert\Desktop\renomeador\renomeadospdf'

# Cria a pasta de saída caso ela ainda não exista
os.makedirs(output_folder, exist_ok=True)

# ============================
# FUNÇÃO: extrair_nome()
# ============================
# Essa função recebe o texto OCR extraído e procura a linha após a palavra "Nome:"
# Ela ignora se a próxima linha for algo como "Função"
def extrair_nome(texto):
    linhas = texto.splitlines()  # Divide o texto em linhas
    for i, linha in enumerate(linhas):
        if 'nome' in linha.lower():  # Procura a palavra "nome" (sem diferenciar maiúsculas/minúsculas)
            if i + 1 < len(linhas):  # Verifica se existe uma linha abaixo
                nome_linha = linhas[i + 1].strip()  # Pega a linha abaixo
                if nome_linha and 'função' not in nome_linha.lower():  # Ignora se for "Função"
                    return nome_linha.title()  # Retorna o nome com letras maiúsculas nas iniciais
    return None  # Se não encontrar, retorna nada

# ============================
# FUNÇÃO: melhorar_imagem()
# ============================
# Esta função melhora a imagem antes do OCR para melhorar a precisão da leitura
def melhorar_imagem(imagem):
    imagem = imagem.convert("L")  # Converte a imagem para tons de cinza
    imagem = imagem.filter(ImageFilter.SHARPEN)  # Aplica nitidez
    imagem = ImageEnhance.Contrast(imagem).enhance(1.5)  # Aumenta o contraste
    return imagem  # Retorna a imagem tratada

# ============================
# PROCESSAMENTO DOS PDFs
# ============================

# Para cada arquivo na pasta de entrada
for filename in os.listdir(input_folder):
    if filename.lower().endswith(".pdf"):  # Verifica se é um arquivo PDF
        pdf_path = os.path.join(input_folder, filename)  # Caminho completo do PDF

        try:
            # Converte APENAS a primeira página do PDF em imagem
            imagens = convert_from_path(
                pdf_path,
                first_page=1,
                last_page=1,
                poppler_path=poppler_path
            )

            if imagens:
                imagem = imagens[0]  # Pega a primeira imagem (página)
                imagem = melhorar_imagem(imagem)  # Aplica filtros de imagem
                texto = pytesseract.image_to_string(imagem, lang='por')  # Faz o OCR em português

                nome = extrair_nome(texto)  # Tenta extrair o nome da imagem

                if nome:
                    novo_nome = f"{nome}.pdf"  # Se achou nome, usa ele como nome do arquivo
                else:
                    novo_nome = f"SEM_NOME_{filename}"  # Caso não consiga extrair o nome

                novo_caminho = os.path.join(output_folder, novo_nome)

                # Evita sobrescrever arquivos com mesmo nome
                contador = 1
                while os.path.exists(novo_caminho):
                    novo_nome = f"{nome}_{contador}.pdf"
                    novo_caminho = os.path.join(output_folder, novo_nome)
                    contador += 1

                # Copia o PDF original para a pasta de saída com o novo nome
                shutil.copy(pdf_path, novo_caminho)
                print(f"✔️ Renomeado: {filename} -> {novo_nome}")
            else:
                print(f"⚠️ Nenhuma imagem extraída de: {filename}")

        except Exception as e:
            print(f"❌ Erro no arquivo {filename}: {e}")

"""Gera ícones em diversos tamanhos a partir de ``icon.png``.

Utilizado para atualizar o diretório ``icons/`` com versões do ícone
compatíveis com diferentes sistemas operacionais.
"""

import os
import sys
from PIL import Image, ImageOps


# Caminho absoluto do diretório onde este script está localizado.
iconDirectory = os.path.abspath(os.path.dirname(sys.argv[0]))

# Carrega a imagem base que será redimensionada.
image = Image.open(os.path.join(iconDirectory, "icon.png"))

# Conjuntos de tamanhos exigidos pelo aplicativo, Linux e macOS.
base = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64)]
linux = [(128, 128), (256, 256), (512, 512), (1024, 1024)]
mac = [(128, 128), (256, 256), (512, 512), (1024, 1024)]

# Cria as imagens base.
for size in base:
    outPath = os.path.join(iconDirectory, "base", f"{size[0]}.png")
    scaledImage = image.resize(size)
    scaledImage.save(outPath)
    print("Ícone criado: " + outPath)

# Cria as imagens para Linux.
for size in linux:
    outPath = os.path.join(iconDirectory, "linux", f"{size[0]}.png")
    scaledImage = image.resize(size)
    scaledImage.save(outPath)
    print("Ícone criado: " + outPath)

# Cria as imagens para macOS, adicionando padding extra.
for size in mac:
    outPath = os.path.join(iconDirectory, "mac", f"{size[0]}.png")

    padFactor = 0.2
    # Reduz a imagem e adiciona bordas para que fique centralizada.
    scale = (int(size[0] * (1 - padFactor)), int(size[1] * (1 - padFactor)))
    scaledImage = image.resize(scale)

    # Calcula o padding necessário em cada direção.
    padAmount = size[0] - scale[0]
    padding = (
        padAmount // 2,
        padAmount // 2,
        padAmount - (padAmount // 2),
        padAmount - (padAmount // 2),
    )
    finalImage = ImageOps.expand(scaledImage, padding)
    finalImage.save(outPath)
    print("Ícone criado: " + outPath)

# Gera o arquivo .ico final com múltiplas resoluções.
new_logo_ico_filename = os.path.join(iconDirectory, "Icon.ico")
new_logo_ico = image.resize((128, 128))
new_logo_ico.save(new_logo_ico_filename, format="ICO", quality=90)
print("Ícone criado: " + new_logo_ico_filename)


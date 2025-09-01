# Paper ECG

[Versão em inglês](README.md)

## Autores
- Natalie Coppa
- Julian Fortune
- Larisa Tereschenko (tereshch@ohsu.edu)

Com ajuda de:
- Kazi Haq
- Hetal Patel

## Visão Geral
Aplicativo que digitaliza imagens de ECG em papel para gerar sinais digitais. Um exemplo de imagem de entrada:

![fullscan](https://user-images.githubusercontent.com/25210657/120732384-13bb9400-c49a-11eb-9913-5e99da0f8d53.png)

Produz sinais como:

![fullscan-output](https://user-images.githubusercontent.com/25210657/120732452-3057cc00-c49a-11eb-8228-0d3f7cb31e78.png)

Para uma descrição dos arquivos de código, consulte [ANALISE_CODIGOS_PTBR.md](docs/ANALISE_CODIGOS_PTBR.md).

## Instalação
Baixe a versão mais recente [aqui](https://github.com/Tereshchenkolab/paper-ecg/releases/latest).

## Guia do Usuário
O guia do usuário (em inglês) está disponível [neste link](USER-GUIDE.md).

## Contribuindo
Siga as instruções de configuração:
- [macOS / Linux](SETUP.md)
- [Windows](SETUP-WINDOWS.md)

Após instalar as dependências e ativar o ambiente virtual, execute:
```
fbs run
```
No Windows pode ser necessário:
```
py -3.6 -m fbs run
```

### Build
Para gerar um executável distribuível:
```
fbs build
```
No Windows pode ser necessário:
```
py -3.6 -m fbs build
```

## Dependências
Requer Python 3.6.7 devido às limitações do `fbs`.

## Citação
Se utilizar este software, cite:
Fortune JD, Coppa NE, Haq KT, Patel H, Tereshchenko LG. Digitizing ECG image: A new method and open-source software code. Computer Methods and Programs in Biomedicine, 2022. DOI: https://doi.org/10.1016/j.cmpb.2022.106890.


# Caçador de Vampiros

Projeto avaliativo de Pensamento Computacional, desenvolvido em Python com Pygame.

## Desenvolvedores

- **[Nome completo do integrante 1]** — RA: [preencher]
- **[Nome completo do integrante 2]** — RA: [preencher]

> Substitua os campos entre colchetes pelos nomes completos e RAs da dupla antes da entrega.

## História

Uma vila está sendo atacada por vampiros. O jogador assume o papel de um caçador que precisa se movimentar pelo cenário e acertar os inimigos com flechas antes que eles o alcancem. Cada acerto aumenta a pontuação e deixa os vampiros mais rápidos.

## Tecnologias

- Python 3
- Pygame
- pyttsx3
- Git e GitHub

## Como executar

Instale as dependências:

```bash
python -m pip install pygame pyttsx3 cx_Freeze
```

Na pasta do projeto, execute:

```bash
python main.py
```

O jogo pede o nome do jogador no terminal antes de abrir a janela.

## Controles

- **Setas:** movimentar o caçador, um eixo por vez
- **CTRL:** disparar uma flecha
- **R:** recarregar até cinco flechas
- **ESPAÇO:** pausar ou continuar
- **X:** iniciar a partida ou tentar novamente
- **ESC:** fechar o jogo

## Estrutura do projeto

- `main.py`: código principal
- `bases/`: imagens, sons e ícones
- `Recursos/trabalho.py`: grava e consulta o recorde
- `log.dat`: histórico criado ao terminar uma partida

## Gerar o executável

```bash
python setup.py build
```

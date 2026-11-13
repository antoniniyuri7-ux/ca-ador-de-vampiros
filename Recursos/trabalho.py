"""Funções simples para salvar as partidas e mostrar o recorde."""

from datetime import datetime


def salvar_partida(caminho, nome, pontuacao):
    """Salva nome, pontos, data e hora no arquivo log.dat."""
    agora = datetime.now()
    data = agora.strftime("%d/%m/%Y")
    hora = agora.strftime("%H:%M:%S")
    arquivo = open(caminho, "a", encoding="utf-8")
    arquivo.write(nome + "\t" + str(pontuacao) + "\t" + data + "\t" + hora + "\n")
    arquivo.close()


def ler_recorde(caminho):
    """Lê o log e devolve o nome, os pontos, a data e a hora da melhor partida."""
    try:
        arquivo = open(caminho, "r", encoding="utf-8")
    except FileNotFoundError:
        return "Ainda não há partidas"

    maior_nome = ""
    maior_pontos = -1
    maior_data = ""
    maior_hora = ""

    for linha in arquivo:
        dados = linha.strip().split("\t")
        if len(dados) == 4:
            nome = dados[0]
            try:
                pontos = int(dados[1])
            except ValueError:
                continue
            data = dados[2]
            hora = dados[3]
            if pontos > maior_pontos:
                maior_nome = nome
                maior_pontos = pontos
                maior_data = data
                maior_hora = hora
    arquivo.close()

    if maior_nome == "":
        return "Ainda não há partidas"
    return maior_nome + " - " + str(maior_pontos) + " pontos (" + maior_data + " " + maior_hora + ")"

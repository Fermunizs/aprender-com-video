---
name: aprender-com-video
description: Use sempre que a pessoa mandar um link do YouTube (vídeo, playlist ou canal), disser "aprende com esse vídeo", "assiste isso", "consome o conteúdo de fulano", "o que esse vídeo ensina", ou quando um estudo depender de vídeos. Lê o vídeo inteiro em texto, cruza com os comentários, guarda o que aprendeu numa base de conhecimento separada por área (negócios, programação, marketing...) e passa a usar esse conhecimento nos trabalhos seguintes.
---

# Aprender com vídeo

A pessoa aprende assistindo. Você aprende lendo o vídeo inteiro, conferindo o que o público respondeu e guardando o que vale num lugar onde você mesmo vai buscar depois. Devolver um resumo e esquecer não é aprender.

## Preparação (uma vez)

- O script é `scripts/video.py`, nesta pasta. Rode com o Python que tem as dependências: se existir `.venv` aqui dentro, use `.venv/bin/python`; senão `python3`. Se faltar dependência, o script avisa (`pip install -r requirements.txt`).
- **Base de conhecimento:** a pasta vem, nesta ordem, de: variável `CONHECIMENTO_DIR`; campo `conhecimento_dir` em `config.json` nesta pasta; senão pergunte uma vez onde guardar e grave em `config.json`. Qualquer pasta de arquivos Markdown serve (um cofre do Obsidian é o caso ideal).

## 1. Trazer o conteúdo (não gasta modelo)

```
python scripts/video.py ler URL [URL...]          # texto completo de cada vídeo
python scripts/video.py comentarios URL 40        # comentários úteis, já filtrados e agrupados
python scripts/video.py canal URL_DO_CANAL 15     # vídeos recentes de um canal ou playlist
python scripts/video.py busca "termo" 10          # procurar vídeos
```

- `ler` devolve título, canal, duração, tamanho e o caminho do texto completo. **Leia o arquivo inteiro**, em blocos se for grande. Nunca trabalhe só com o começo, o título ou a descrição. Se o leitor de arquivos atrapalhar, leia pelo terminal em pedaços: o problema da ferramenta não é motivo para parar.
- Rode `comentarios` em todo vídeo que for virar conhecimento.
- "Consome o conteúdo de fulano": liste o canal, escolha os vídeos que mais servem ao objetivo da pessoa (os mais vistos e os recentes sobre o tema), diga quais escolheu e por quê, e leia pelo menos 5.
- Vídeo falhou (privado, sem legenda e sem chave de transcrição): tente outro do mesmo autor sobre o mesmo assunto antes de relatar a falha.

## 2. Aprender de verdade

De cada vídeo, tire:

1. **A tese** em duas linhas: o que o autor defende, para quem e em que contexto (país, ano, orçamento, plataforma).
2. **As técnicas**, cada uma com nome, passo a passo e os números ditos (orçamento, margem, prazo, métrica, ferramenta, exemplo).
3. **Os exemplos concretos** mostrados.
4. **O que é venda** do curso, da mentoria ou do produto do autor, separado do que é conteúdo aproveitável. Promessa ("fature X por mês") não entra como fato.
5. **O que os comentários acrescentam** (veja `references/comentarios.md`): correções, o que ficou sem explicar, quem tentou e o que aconteceu.
6. **O que vale para a pessoa agora:** ligue cada técnica a um projeto ou objetivo dela e diga o que muda no contexto dela.
7. **Onde você desconfia** e o que precisaria conferir antes de aplicar.

## 3. Classificar por área

Todo aprendizado entra numa área. Use as de `references/areas.md` (Negócios e vendas, Marketing e conteúdo, Programação, IA e automação, Design, Finanças, Carreira e produtividade, Outros) e, dentro da área, um assunto (ex.: Negócios e vendas → dropshipping). Vídeo que cobre duas áreas: a nota fica na principal e o manual da outra ganha um link.

## 4. Guardar na base de conhecimento

Estrutura (modelos em `references/modelos.md`):

```
<base>/
  Índice.md                              uma linha por área e por manual
  <Área>/
    Manual — <assunto>.md                o que você sabe sobre o assunto, acumulado
    Vídeos/AAAA-MM-DD — Canal — Título.md   uma nota por vídeo
```

- **Nota do vídeo:** fonte, tese, técnicas, exemplos, o que os comentários dizem, o que é venda, o que vamos usar.
- **Manual do assunto:** é o que importa. A cada vídeo, acrescente as técnicas novas na seção certa, com link para a nota de origem. Se o vídeo contradiz o manual, registre as duas versões, qual você seguiria e por quê. Técnica confirmada por mais de uma fonte ou por comentários de quem aplicou ganha a marca "confirmada"; a que só uma fonte afirma fica como "a testar".
- Atualize o `Índice.md`.
- Não cole a transcrição na base: guarde o aprendizado com as suas palavras e o link do vídeo.

## 5. Usar

- **Antes de trabalhar num assunto, leia o manual dele.** Diga de qual vídeo veio a técnica que está aplicando.
- Depois de aprender, escolha **uma técnica para aplicar agora** no projeto da pessoa e faça o primeiro passo, ou deixe pronto o que depender dela.
- Quando aplicar e der certo ou errado, volte ao manual e anote o resultado. É assim que a base fica melhor que os vídeos.

## 6. O que responder

Em até 10 linhas: o que o vídeo ensina de útil (3 a 5 pontos com número), o que é só venda, o que os comentários corrigem ou confirmam, a técnica que você já começou a aplicar, e onde ficou a nota e o manual. No fim, o placar honesto: quantos vídeos leu inteiros, quantas palavras, quantos comentários considerou e o que falhou.

## Limites

- Nunca diga que leu, assistiu ou estudou o que não leu inteiro.
- Não reproduza a transcrição nem trechos longos para terceiros: é conteúdo do autor.
- Vídeo é opinião de alguém com interesse próprio. Trate como hipótese até cruzar com outra fonte, com os comentários ou com um teste.

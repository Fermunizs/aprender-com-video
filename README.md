# aprender-com-video

Uma skill para agentes de IA (Claude Code, Hermes e qualquer agente que leia `SKILL.md`) aprenderem com vídeos do YouTube do jeito que a gente aprende assistindo: o agente lê o vídeo inteiro, confere o que o público respondeu nos comentários, guarda o que vale numa base de conhecimento separada por área e passa a usar isso nos trabalhos seguintes.

Eu consumo muito vídeo e o meu agente não aprendia junto comigo. Ele recebia o link, devolvia um resumo genérico e na conversa seguinte já não sabia de nada. Esta skill resolve isso.

## O que ela faz

- **Lê o vídeo inteiro em texto.** Usa a legenda do YouTube; quando o vídeo não tem legenda, baixa só o áudio e transcreve. Um vídeo de 21 minutos sai em 2 segundos e ocupa cerca de 6 mil tokens.
- **Aprende com os comentários.** Tira spam, divulgação e elogio vazio, e separa o que sobra em críticas e correções, resultados de quem tentou, perguntas (o que o vídeo não explicou) e mais curtidos. Crítica com 3 curtidas costuma ensinar mais que elogio com 600.
- **Separa conteúdo de venda.** Curso, mentoria e promessa de faturamento não entram como fato.
- **Guarda por área.** Negócios e vendas, Marketing e conteúdo, Programação, IA e automação, Design, Finanças, Carreira e produtividade. Cada assunto tem um manual que cresce a cada vídeo, com as técnicas marcadas como confirmada, a testar ou não funcionou.
- **Usa o que aprendeu.** Antes de trabalhar num assunto o agente lê o manual, e depois de aplicar uma técnica anota o resultado.

Buscar, transcrever e ler comentários não chama modelo nenhum. Você só gasta tokens quando o agente lê o texto.

## Instalação

Precisa de Python 3.10 ou mais novo.

```bash
git clone https://github.com/Fermunizs/aprender-com-video.git
cd aprender-com-video
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Depois copie (ou faça um link) da pasta para onde o seu agente procura skills:

| Agente | Pasta |
|---|---|
| Claude Code | `~/.claude/skills/aprender-com-video/` |
| Hermes Agent | `~/.hermes/skills/aprender-com-video/` |
| Outros | onde ele lê `SKILL.md`; ou cole o conteúdo do `SKILL.md` nas instruções |

```bash
cp -R ../aprender-com-video ~/.claude/skills/aprender-com-video
```

### Onde guardar o conhecimento

Crie `config.json` dentro da pasta da skill com o caminho da sua base. Qualquer pasta de arquivos Markdown serve; um cofre do Obsidian é o melhor caso, porque os links entre notas funcionam.

```json
{ "conhecimento_dir": "/caminho/para/o/seu/cofre/Conhecimento" }
```

Também vale a variável de ambiente `CONHECIMENTO_DIR`. Sem nenhuma das duas, o agente pergunta uma vez e grava o arquivo.

### Vídeos sem legenda (opcional)

Para transcrever pelo áudio você precisa de:

- `ffmpeg` instalado (`brew install ffmpeg`, `apt install ffmpeg`), ou a variável `FFMPEG` apontando para o executável;
- uma chave gratuita da Groq em `GROQ_API_KEY` (https://console.groq.com). O áudio vai para a Groq para ser transcrito.

Sem isso, a skill funciona normalmente com os vídeos que têm legenda, que são a grande maioria.

## Como usar

Fale com o agente:

- "aprende com esse vídeo: https://www.youtube.com/watch?v=..."
- "consome o canal de fulano sobre dropshipping e me diz o que dá para aplicar na minha loja"
- "o que os comentários desse vídeo dizem que ele não mostrou?"
- "antes de mexer no anúncio, vê o que a gente já aprendeu sobre copy"

Ou use o script direto:

```bash
.venv/bin/python scripts/video.py ler https://www.youtube.com/watch?v=ID
.venv/bin/python scripts/video.py comentarios https://www.youtube.com/watch?v=ID 40
.venv/bin/python scripts/video.py canal https://www.youtube.com/@canal 15
.venv/bin/python scripts/video.py busca "dropshipping reino unido" 10
```

## Como fica a base de conhecimento

```
Conhecimento/
  Índice.md
  Negócios e vendas/
    Manual — dropshipping.md
    Vídeos/
      2026-10-08 — Canal — Primeira venda orgânica.md
  Programação/
    Manual — Next.js.md
    Vídeos/
```

O manual é o que importa. Ele junta o que vários vídeos disseram, registra onde as fontes discordam, lista o que ainda falta descobrir e guarda o que aconteceu quando você aplicou. Os modelos de nota estão em `references/modelos.md`.

## O que tem no repositório

| Arquivo | Para que serve |
|---|---|
| `SKILL.md` | As instruções que o agente segue |
| `scripts/video.py` | Transcrição, comentários filtrados, lista de canal e busca |
| `references/comentarios.md` | Como ler comentários: o que vale, o que é plateia |
| `references/areas.md` | As áreas e como classificar |
| `references/modelos.md` | Modelos da nota de vídeo, do manual e do índice |

## Limites e cuidados

- A skill guarda o aprendizado, não a transcrição. O conteúdo do vídeo é do autor: não republique o texto dele.
- Legenda automática erra nomes e números. O agente é instruído a tratar o vídeo como hipótese até cruzar com outra fonte, com os comentários ou com um teste.
- O filtro de comentários é por regras simples (tamanho, padrões de spam, palavras de sinal), em português e inglês. Ele reduz ruído, não julga verdade; quem julga é o agente, seguindo `references/comentarios.md`.
- O YouTube às vezes bloqueia a leitura de legendas a partir de servidores na nuvem. No computador de casa funciona.
- Ele lê os 300 comentários do topo, não todos.

## Licença

MIT. Use, adapte e compartilhe.

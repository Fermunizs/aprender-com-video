#!/usr/bin/env python3
"""Traz vídeos do YouTube em texto para um agente de IA ler e aprender.

  video.py ler URL [URL...]            transcreve cada vídeo e guarda o texto (legenda; sem legenda, áudio + Whisper)
  video.py comentarios URL [N]         os N comentários mais úteis (padrão 40), já filtrados de spam e elogio vazio
  video.py canal URL [N]               lista os N vídeos mais recentes de um canal ou playlist (padrão 15)
  video.py busca "termo" [N]           procura vídeos no YouTube (padrão 10)

Nenhum comando chama modelo de IA. O texto fica em cache (padrão ~/.cache/aprender-com-video,
ou a pasta em APRENDER_VIDEO_CACHE) e é apagado depois de 30 dias.
Vídeo sem legenda precisa de ffmpeg e de GROQ_API_KEY (transcrição gratuita pelo Whisper da Groq).
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import time
import urllib.request
import uuid
from pathlib import Path

try:
    import yt_dlp
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    sys.exit("Faltam dependências. Rode: pip install -r requirements.txt (de preferência num ambiente virtual).")

CACHE = Path(os.getenv("APRENDER_VIDEO_CACHE") or Path.home() / ".cache" / "aprender-com-video")
LANGS = ["pt", "pt-BR", "en", "en-GB", "en-US", "es"]
GROQ_LIMIT_BYTES = 24 * 1024 * 1024
CHUNK_SECONDS = 1200
KEEP_DAYS = 30
WRAP_CHARS = 160
QUIET = {"quiet": True, "no_warnings": True, "noprogress": True}

# Comentário que não ensina nada: divulgação, corrente, golpe e elogio vazio.
SPAM = re.compile(r"(?i)whats?app|telegram|t\.me/|wa\.me/|bit\.ly|pix\b|ganhe? dinheiro|renda extra|me segue|inscreva|sorteio|\+?\d{2}\s?\(?\d{2}\)?\s?9?\d{4}-?\d{4}|https?://")
PRAISE = re.compile(r"(?i)^(top|muito bom|[óo]timo( v[ií]deo)?|excelente|parab[ée]ns|show|gratid[ãa]o|amei|perfeito|great video|nice|thanks?|obrigad[oa]|melhor canal|aula|brabo|sensacional)[\s!.,❤👏🔥🙏]*$")
SIGNALS = {
    "resultado": re.compile(r"(?i)funcionou|deu certo|consegui|vendi|faturei|testei|apliquei|fiz (isso|igual)|primeira venda|worked|i made|i tried|n[ãa]o (deu|funcionou|consegui)|didn'?t work|perdi"),
    "correção": re.compile(r"(?i)na verdade|errado|incorreto|desatualizado|mudou|n[ãa]o [ée] (bem )?assim|cuidado|golpe|mentira|enganoso|actually|outdated|wrong|scam|misleading|faltou"),
    "pergunta": re.compile(r"\?"),
}
MIN_COMMENT_CHARS = 40


def ffmpeg():
    return os.getenv("FFMPEG") or shutil.which("ffmpeg")


def video_id(url):
    match = re.search(r"(?:v=|youtu\.be/|shorts/|live/|embed/)([\w-]{11})", url)
    return match.group(1) if match else (url if re.fullmatch(r"[\w-]{11}", url) else None)


def watch(vid):
    return f"https://www.youtube.com/watch?v={vid}"


def info(vid):
    with yt_dlp.YoutubeDL({**QUIET, "skip_download": True}) as ydl:
        return ydl.extract_info(watch(vid), download=False)


def captions(vid):
    try:
        listing = YouTubeTranscriptApi().list(vid)
        try:
            track = listing.find_transcript(LANGS)
        except Exception:
            track = next(iter(listing))
        text = " ".join(getattr(part, "text", None) or part["text"] for part in track.fetch())
        return " ".join(text.split()), f"legenda do YouTube ({track.language_code}{', automática' if track.is_generated else ''})"
    except Exception:
        return None, None


def whisper(path):
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        raise RuntimeError("vídeo sem legenda: defina GROQ_API_KEY para transcrever o áudio")
    boundary = uuid.uuid4().hex
    fields = (("model", "whisper-large-v3-turbo"), ("response_format", "text"))
    parts = [f'--{boundary}\r\nContent-Disposition: form-data; name="{n}"\r\n\r\n{v}\r\n'.encode() for n, v in fields]
    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="a.mp3"\r\nContent-Type: audio/mpeg\r\n\r\n'.encode())
    parts.append(Path(path).read_bytes())
    parts.append(f"\r\n--{boundary}--\r\n".encode())
    request = urllib.request.Request(
        "https://api.groq.com/openai/v1/audio/transcriptions",
        b"".join(parts),
        {"authorization": f"Bearer {key}", "content-type": f"multipart/form-data; boundary={boundary}", "user-agent": "curl/8"},
    )
    with urllib.request.urlopen(request, timeout=300) as response:
        return " ".join(response.read().decode().split())


def from_audio(vid):
    """Sem legenda: baixa só o áudio, comprime, corta em pedaços de 20 minutos e transcreve."""
    tool = ffmpeg()
    if not tool:
        raise RuntimeError("vídeo sem legenda: instale o ffmpeg para converter o áudio")
    base = CACHE / f"{vid}-audio"
    with yt_dlp.YoutubeDL({**QUIET, "format": "bestaudio/best", "outtmpl": str(base) + ".%(ext)s"}) as ydl:
        ydl.download([watch(vid)])
    source = next(iter(glob.glob(str(base) + ".*")), None)
    if not source:
        raise RuntimeError("não consegui baixar o áudio")
    pattern = str(CACHE / f"{vid}-parte-%03d.mp3")
    subprocess.run([tool, "-y", "-i", source, "-vn", "-ac", "1", "-ar", "16000", "-b:a", "32k", "-f", "segment", "-segment_time", str(CHUNK_SECONDS), pattern], capture_output=True, timeout=1800, check=False)
    os.remove(source)
    pieces = sorted(glob.glob(str(CACHE / f"{vid}-parte-*.mp3")))
    try:
        if not pieces:
            raise RuntimeError("não consegui converter o áudio")
        text = " ".join(whisper(piece) for piece in pieces if os.path.getsize(piece) <= GROQ_LIMIT_BYTES)
        return text, f"áudio transcrito pelo Whisper ({len(pieces)} {'parte' if len(pieces) == 1 else 'partes'})"
    finally:
        for piece in pieces:
            os.remove(piece)


def cmd_ler(url):
    vid = video_id(url)
    if not vid:
        print(f"\n✗ {url}\n  não reconheci como vídeo do YouTube")
        return
    try:
        meta = info(vid)
    except Exception as exc:
        meta = {}
        print(f"  (sem os dados do vídeo: {str(exc)[:120]})")
    text, how = captions(vid)
    if not text:
        try:
            text, how = from_audio(vid)
        except Exception as exc:
            print(f"\n✗ {meta.get('title') or url}\n  {str(exc)[:240]}")
            return
    minutes = round((meta.get("duration") or 0) / 60)
    channel = meta.get("channel") or meta.get("uploader", "?")
    header = (
        f"Título: {meta.get('title', '?')}\nCanal: {channel}\nPublicado: {meta.get('upload_date', '?')}\nDuração: {minutes} min\n"
        f"Visualizações: {meta.get('view_count', '?')}\nURL: {watch(vid)}\nOrigem do texto: {how}\n"
    )
    path = CACHE / f"{vid}.txt"
    # Linhas curtas: leitores de arquivo de agentes costumam cortar linha comprida demais.
    path.write_text(header + "\n" + "\n".join(textwrap.wrap(text, WRAP_CHARS)) + "\n")
    words, lines = len(text.split()), len(path.read_text().splitlines())
    print(f"\n✓ {meta.get('title', vid)}\n  canal: {channel} · {minutes} min · {words} palavras (~{round(words * 1.4 / 1000)} mil tokens) · {how}")
    print(f"  texto completo: {path} ({lines} linhas; leia todas)")
    if meta.get("description"):
        print(f"  descrição: {' '.join(meta['description'].split())[:300]}")


def useful(comment):
    text = " ".join((comment.get("text") or "").split())
    if len(text) < MIN_COMMENT_CHARS or SPAM.search(text) or PRAISE.match(text):
        return None
    letters = sum(ch.isalpha() for ch in text)
    if letters < len(text) * 0.5:  # quase só emoji, número ou símbolo
        return None
    return text


def cmd_comentarios(url, count):
    vid = video_id(url)
    if not vid:
        print("não reconheci como vídeo do YouTube")
        return
    options = {**QUIET, "skip_download": True, "getcomments": True, "extractor_args": {"youtube": {"max_comments": ["300", "300", "0", "0"], "comment_sort": ["top"]}}}
    with yt_dlp.YoutubeDL(options) as ydl:
        data = ydl.extract_info(watch(vid), download=False)
    raw = data.get("comments") or []
    seen, kept = set(), []
    for comment in raw:
        text = useful(comment)
        if not text or text.lower()[:80] in seen:
            continue
        seen.add(text.lower()[:80])
        kinds = [name for name, pattern in SIGNALS.items() if pattern.search(text)]
        weight = (comment.get("like_count") or 0) + (40 if comment.get("is_pinned") else 0) + (25 if comment.get("is_favorited") else 0) + (15 if kinds and kinds != ["pergunta"] else 0)
        kept.append((weight, comment, text, kinds))
    kept.sort(key=lambda item: -item[0])

    def render(item):
        _, comment, text, kinds = item
        marks = [f"{comment.get('like_count') or 0} curtidas"]
        if comment.get("is_pinned"):
            marks.append("fixado")
        if comment.get("is_favorited"):
            marks.append("coração do autor")
        if comment.get("author_is_uploader"):
            marks.append("do próprio autor")
        return f"[{' · '.join(marks)}] {text[:600]}"

    # Crítica e correção ensinam mais que elogio, mesmo com poucas curtidas: por isso vêm primeiro e em seção própria.
    groups = [
        ("Críticas, correções e avisos", [k for k in kept if "correção" in k[3]]),
        ("Resultados relatados por quem tentou", [k for k in kept if "resultado" in k[3] and "correção" not in k[3]]),
        ("Perguntas (o que ficou sem explicar)", [k for k in kept if k[3] == ["pergunta"]]),
        ("Mais curtidos", [k for k in kept if not k[3]]),
    ]
    per_group = max(3, count // len(groups))
    lines = [f"Comentários de: {data.get('title')}", f"URL: {watch(vid)}", f"{len(raw)} lidos, {len(kept)} úteis depois do filtro de spam e elogio vazio."]
    for title, items in groups:
        if items:
            lines += ["", f"## {title} ({len(items)})"] + [render(item) for item in items[:per_group]]
    path = CACHE / f"{vid}-comentarios.txt"
    path.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nsalvo em {path}")


def cmd_lista(target, count):
    with yt_dlp.YoutubeDL({**QUIET, "extract_flat": True, "playlistend": count}) as ydl:
        data = ydl.extract_info(target, download=False)
    for entry in (data.get("entries") or [])[:count]:
        minutes = round((entry.get("duration") or 0) / 60)
        views = entry.get("view_count")
        print(f"{watch(entry.get('id'))} · {minutes} min{f' · {views} views' if views else ''} · {entry.get('title')}")


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    for old in CACHE.glob("*"):
        if old.is_file() and time.time() - old.stat().st_mtime > KEEP_DAYS * 86400:
            old.unlink()
    args = sys.argv[1:]
    number = lambda index, default: int(args[index]) if len(args) > index and args[index].isdigit() else default  # noqa: E731
    if len(args) >= 2 and args[0] == "ler":
        for url in args[1:]:
            cmd_ler(url)
    elif len(args) >= 2 and args[0] == "comentarios":
        cmd_comentarios(args[1], number(2, 40))
    elif len(args) >= 2 and args[0] == "canal":
        url = args[1] if "/videos" in args[1] or "list=" in args[1] else args[1].rstrip("/") + "/videos"
        cmd_lista(url, number(2, 15))
    elif len(args) >= 2 and args[0] == "busca":
        count = number(2, 10)
        cmd_lista(f"ytsearch{count}:{args[1]}", count)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()

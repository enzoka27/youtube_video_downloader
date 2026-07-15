# YouTube Downloader

*[Português](#português) · [English](#english)*

---

## Português

Um baixador de vídeos e áudios do YouTube com interface gráfica simples (Tkinter). Cole a URL, escolha o formato e a qualidade, e baixe.

## Recursos

- Interface gráfica leve, sem terminal.
- Vídeo em **MP4**, **MKV** ou **WEBM**.
- Áudio em **MP3**, **M4A**, **WAV**, **OPUS** ou **FLAC**.
- Seleção de qualidade (até 2160p para vídeo, até 320 kbps para áudio).
- Pasta de destino fixa (opcional) ou perguntada a cada download.
- Baixa automaticamente o **yt-dlp** e o **ffmpeg** se não estiverem instalados.

## Como usar

### Opção 1 — Executável (Windows)

Baixe e execute `dist/YouTube Downloader.exe`. Não precisa instalar Python.

### Opção 2 — Rodar o script

Requer [Python 3](https://www.python.org/downloads/) (o Tkinter já vem incluído).

```bash
python main.py
```

Na primeira execução, o programa oferece baixar o `yt-dlp` (~15 MB) e o `ffmpeg` (~100 MB) automaticamente, salvando-os na pasta do programa.

## Uso

1. Cole a URL do vídeo.
2. Escolha o formato (vídeo ou áudio).
3. Escolha a qualidade.
4. (Opcional) Defina uma pasta de destino fixa.
5. Clique em **Baixar**.

## Observações

- O **ffmpeg** é necessário para vídeos em 1080p+ (junção de vídeo e áudio) e para conversão de áudio (MP3, WAV, FLAC, OPUS).
- Multiplataforma: Windows, Linux e macOS (os binários de yt-dlp/ffmpeg corretos são baixados conforme o sistema).

---

## English

A YouTube video and audio downloader with a simple graphical interface (Tkinter). Paste the URL, pick the format and quality, and download.

### Features

- Lightweight GUI, no terminal needed.
- Video in **MP4**, **MKV** or **WEBM**.
- Audio in **MP3**, **M4A**, **WAV**, **OPUS** or **FLAC**.
- Quality selection (up to 2160p for video, up to 320 kbps for audio).
- Fixed destination folder (optional), or asked on every download.
- Automatically downloads **yt-dlp** and **ffmpeg** if they aren't installed.

### Getting started

#### Option 1 — Executable (Windows)

Download and run `dist/YouTube Downloader.exe`. No Python installation required.

#### Option 2 — Run the script

Requires [Python 3](https://www.python.org/downloads/) (Tkinter is already included).

```bash
python main.py
```

On first run, the program offers to automatically download `yt-dlp` (~15 MB) and `ffmpeg` (~100 MB), saving them into the program's folder.

### Usage

1. Paste the video URL.
2. Choose the format (video or audio).
3. Choose the quality.
4. (Optional) Set a fixed destination folder.
5. Click **Baixar** (Download).

### Notes

- **ffmpeg** is required for 1080p+ videos (merging video and audio) and for audio conversion (MP3, WAV, FLAC, OPUS).
- Cross-platform: Windows, Linux and macOS (the correct yt-dlp/ffmpeg binaries are downloaded per system).
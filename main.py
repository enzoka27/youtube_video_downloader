import os
import sys
import shutil
import platform
import subprocess
import tarfile
import tempfile
import threading
import urllib.request
import zipfile
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

YTDLP_URLS = {
    "Windows": "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe",
    "Linux":   "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp",
    "Darwin":  "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_macos",
}

FFMPEG_URLS = {
    "Windows": "https://github.com/BtbN/FFmpeg-Builds/releases/latest/download/ffmpeg-master-latest-win64-gpl.zip",
    "Linux":   "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz",
    "Darwin":  "https://evermeet.cx/ffmpeg/getrelease/zip",
}

def diretorio_app():
    #Pasta do script (ou do .exe, quando compilado com PyInstaller)
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _caminho(nome_win, nome_unix):
    nome = nome_win if platform.system() == "Windows" else nome_unix
    return os.path.join(diretorio_app(), nome)


def caminho_local_ytdlp():
    return _caminho("yt-dlp.exe", "yt-dlp")


def caminho_local_ffmpeg():
    return _caminho("ffmpeg.exe", "ffmpeg")

class JanelaProgresso:
    #Popup com barra de progresso com reporthook do urlretrieve

    def __init__(self, titulo):
        self.janela = tk.Toplevel()
        self.janela.title(titulo)
        self.janela.resizable(False, False)

        w, h = 380, 110
        self.janela.update_idletasks()
        x = (self.janela.winfo_screenwidth() - w) // 2
        y = (self.janela.winfo_screenheight() - h) // 2
        self.janela.geometry(f"{w}x{h}+{x}+{y}")

        self.lbl = ttk.Label(self.janela, text="Iniciando…")
        self.lbl.pack(pady=(15, 8))
        self.pb = ttk.Progressbar(self.janela, mode="determinate", length=340)
        self.pb.pack(padx=20)
        self.janela.update()

    def hook(self, blocos, tam_bloco, tam_total):
        if tam_total > 0:
            baixado = blocos * tam_bloco
            pct = min(100, baixado * 100 / tam_total)
            self.pb["value"] = pct
            mb_b = baixado / (1024 * 1024)
            mb_t = tam_total / (1024 * 1024)
            self.lbl.config(text=f"{mb_b:.1f} MB / {mb_t:.1f} MB  ({pct:.0f}%)")
            self.janela.update()

    def status(self, texto):
        #Troca pra modo indeterminado (ex.: durante a extração)
        self.pb.stop()
        self.pb["mode"] = "indeterminate"
        self.pb.start(10)
        self.lbl.config(text=texto)
        self.janela.update()

    def fechar(self):
        try:
            self.pb.stop()
        except tk.TclError:
            pass
        self.janela.destroy()

def encontrar_ytdlp():
    local = caminho_local_ytdlp()
    if os.path.isfile(local):
        return local
    return shutil.which("yt-dlp")


def baixar_ytdlp():
    sistema = platform.system()
    url = YTDLP_URLS.get(sistema)
    if not url:
        return None, f"Sistema não suportado: {sistema}"

    destino = caminho_local_ytdlp()
    progresso = JanelaProgresso("Baixando yt-dlp")
    try:
        urllib.request.urlretrieve(url, destino, reporthook=progresso.hook)
        if sistema != "Windows":
            os.chmod(destino, 0o755)
        return destino, None
    except Exception as e:
        return None, str(e)
    finally:
        progresso.fechar()


def garantir_ytdlp():
    caminho = encontrar_ytdlp()
    if caminho:
        return caminho

    resposta = messagebox.askyesno(
        "yt-dlp não encontrado",
        "O yt-dlp não está instalado no seu sistema.\n\n"
        "Deseja baixar agora? (~15 MB, do GitHub oficial, salvo na pasta do programa.)"
    )
    if not resposta:
        return None

    caminho, erro = baixar_ytdlp()
    if erro:
        messagebox.showerror("Falha ao baixar yt-dlp", erro)
        return None
    return caminho

def encontrar_ffmpeg():
    local = caminho_local_ffmpeg()
    if os.path.isfile(local):
        return local
    return shutil.which("ffmpeg")


def _extrair_ffmpeg(arquivo_baixado, destino_final):
    #Extrai só o binário ffmpeg do pacote baixado (zip/tar.xz)
    sistema = platform.system()

    if sistema == "Windows":
        #zip do BtbN: contém ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe
        with zipfile.ZipFile(arquivo_baixado) as zf:
            alvos = [n for n in zf.namelist()
                     if n.replace("\\", "/").endswith("/bin/ffmpeg.exe")]
            if not alvos:
                raise RuntimeError("ffmpeg.exe não encontrado no zip.")
            with zf.open(alvos[0]) as src, open(destino_final, "wb") as dst:
                shutil.copyfileobj(src, dst)

    elif sistema == "Linux":
        #tar.xz do johnvansickle: contém ffmpeg-*/ffmpeg
        with tarfile.open(arquivo_baixado, "r:xz") as tf:
            alvos = [m for m in tf.getmembers()
                     if m.isfile() and m.name.endswith("/ffmpeg")]
            if not alvos:
                raise RuntimeError("ffmpeg não encontrado no tar.xz.")
            with tf.extractfile(alvos[0]) as src, open(destino_final, "wb") as dst:
                shutil.copyfileobj(src, dst)
        os.chmod(destino_final, 0o755)

    elif sistema == "Darwin":
        #zip do evermeet.cx: contém o binário ffmpeg direto na raiz
        with zipfile.ZipFile(arquivo_baixado) as zf:
            alvos = [n for n in zf.namelist()
                     if n.endswith("ffmpeg") and not n.endswith("/")]
            if not alvos:
                raise RuntimeError("ffmpeg não encontrado no zip.")
            with zf.open(alvos[0]) as src, open(destino_final, "wb") as dst:
                shutil.copyfileobj(src, dst)
        os.chmod(destino_final, 0o755)


def baixar_ffmpeg():
    sistema = platform.system()
    url = FFMPEG_URLS.get(sistema)
    if not url:
        return None, f"Sistema não suportado: {sistema}"

    destino_final = caminho_local_ffmpeg()
    sufixo = ".zip" if sistema in ("Windows", "Darwin") else ".tar.xz"

    #baixa o pacote inteiro pra um arquivo temporário, extrai só o binário
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=sufixo)
    os.close(tmp_fd)

    progresso = JanelaProgresso("Baixando ffmpeg")
    try:
        urllib.request.urlretrieve(url, tmp_path, reporthook=progresso.hook)
        progresso.status("Extraindo…")
        _extrair_ffmpeg(tmp_path, destino_final)
        return destino_final, None
    except Exception as e:
        return None, str(e)
    finally:
        progresso.fechar()
        try:
            os.remove(tmp_path)
        except OSError:
            pass


def garantir_ffmpeg():
    caminho = encontrar_ffmpeg()
    if caminho:
        return caminho

    resposta = messagebox.askyesno(
        "ffmpeg não encontrado",
        "O ffmpeg é necessário pra:\n"
        "  • Juntar vídeo + áudio em qualidades altas (1080p+)\n"
        "  • Converter áudio pra MP3, WAV, FLAC, OPUS…\n\n"
        "Deseja baixar agora? (~100 MB, salvo na pasta do programa.)"
    )
    if not resposta:
        return None

    caminho, erro = baixar_ffmpeg()
    if erro:
        messagebox.showerror("Falha ao baixar ffmpeg", erro)
        return None
    return caminho

FORMATOS = {
    "Vídeo — MP4":  {"tipo": "video", "ext": "mp4"},
    "Vídeo — MKV":  {"tipo": "video", "ext": "mkv"},
    "Vídeo — WEBM": {"tipo": "video", "ext": "webm"},
    "Áudio — MP3":  {"tipo": "audio", "ext": "mp3"},
    "Áudio — M4A":  {"tipo": "audio", "ext": "m4a"},
    "Áudio — WAV":  {"tipo": "audio", "ext": "wav"},
    "Áudio — OPUS": {"tipo": "audio", "ext": "opus"},
    "Áudio — FLAC": {"tipo": "audio", "ext": "flac"},
}

QUALIDADES = {
    "video": ["Melhor disponível", "2160", "1440", "1080", "720", "480", "360"],
    "audio": ["Melhor disponível", "320", "256", "192", "128", "96"],
}


def montar_comando(ytdlp, ffmpeg, url, formato_label, qualidade, pasta):
    cfg = FORMATOS[formato_label]
    cmd = [ytdlp]

    #aponta o ffmpeg local (senão o yt-dlp só acha ele se estiver no PATH)
    if ffmpeg:
        cmd += ["--ffmpeg-location", ffmpeg]

    if cfg["tipo"] == "video":
        if qualidade == "Melhor disponível":
            seletor = "bv*+ba/b"
        else:
            seletor = f"bv*[height<={qualidade}]+ba/b[height<={qualidade}]"
        cmd += ["-f", seletor, "--merge-output-format", cfg["ext"]]
    else:  #audio
        cmd += ["-x", "--audio-format", cfg["ext"]]
        if qualidade != "Melhor disponível":
            cmd += ["--audio-quality", f"{qualidade}K"]

    cmd += ["-o", os.path.join(pasta, "%(title)s.%(ext)s"), url]
    return cmd

class App(tk.Tk):
    def __init__(self, ytdlp_path, ffmpeg_path):
        super().__init__()
        self.ytdlp_path = ytdlp_path
        self.ffmpeg_path = ffmpeg_path
        self.title("YouTube Downloader")
        self.geometry("540x460")
        self.resizable(False, False)

        pad = {"padx": 20}

        ttk.Label(self, text="URL do vídeo:").pack(anchor="w", pady=(20, 4), **pad)
        self.url_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.url_var).pack(fill="x", **pad)

        ttk.Label(self, text="Formato:").pack(anchor="w", pady=(16, 4), **pad)
        self.formato_var = tk.StringVar(value="Vídeo — MP4")
        self.cb_formato = ttk.Combobox(
            self, textvariable=self.formato_var,
            values=list(FORMATOS.keys()), state="readonly"
        )
        self.cb_formato.pack(fill="x", **pad)
        self.cb_formato.bind("<<ComboboxSelected>>", self._atualizar_qualidades)

        ttk.Label(self, text="Qualidade:").pack(anchor="w", pady=(16, 4), **pad)
        self.qualidade_var = tk.StringVar(value="Melhor disponível")
        self.cb_qualidade = ttk.Combobox(
            self, textvariable=self.qualidade_var,
            values=QUALIDADES["video"], state="readonly"
        )
        self.cb_qualidade.pack(fill="x", **pad)

        ttk.Label(
            self, text="Pasta de destino (opcional):"
        ).pack(anchor="w", pady=(16, 4), **pad)
        self.pasta_var = tk.StringVar()
        linha_pasta = ttk.Frame(self)
        linha_pasta.pack(fill="x", **pad)
        ttk.Entry(
            linha_pasta, textvariable=self.pasta_var
        ).pack(side="left", fill="x", expand=True)
        ttk.Button(
            linha_pasta, text="Procurar…", command=self._escolher_pasta
        ).pack(side="left", padx=(8, 0))
        ttk.Label(
            self,
            text="Se vazio, o programa pergunta a cada download.",
            foreground="gray"
        ).pack(anchor="w", **pad)

        self.btn = ttk.Button(self, text="Baixar", command=self._iniciar)
        self.btn.pack(pady=20)

        self.status_var = tk.StringVar(value="Pronto.")
        ttk.Label(self, textvariable=self.status_var, foreground="gray").pack()

    def _atualizar_qualidades(self, _event=None):
        tipo = FORMATOS[self.formato_var.get()]["tipo"]
        valores = QUALIDADES[tipo]
        self.cb_qualidade["values"] = valores
        if self.qualidade_var.get() not in valores:
            self.qualidade_var.set(valores[0])

    def _escolher_pasta(self):
        pasta = filedialog.askdirectory(title="Pasta de destino")
        if pasta:
            self.pasta_var.set(pasta)

    def _iniciar(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Atenção", "Cole a URL do vídeo primeiro.")
            return

        #usa a pasta fixa se o usuário definiu; senão, pergunta a cada download
        pasta = self.pasta_var.get().strip()
        if pasta:
            if not os.path.isdir(pasta):
                messagebox.showwarning(
                    "Atenção",
                    "A pasta de destino informada não existe.\n"
                    "Escolha uma pasta válida."
                )
                return
        else:
            pasta = filedialog.askdirectory(title="Onde salvar?")
            if not pasta:
                return

        self.btn.config(state="disabled")
        self.status_var.set("Baixando…")
        threading.Thread(
            target=self._baixar,
            args=(url, self.formato_var.get(), self.qualidade_var.get(), pasta),
            daemon=True
        ).start()

    def _baixar(self, url, formato, qualidade, pasta):
        cmd = montar_comando(
            self.ytdlp_path, self.ffmpeg_path,
            url, formato, qualidade, pasta
        )
        try:
            resultado = subprocess.run(cmd, capture_output=True, text=True)
            if resultado.returncode == 0:
                self.status_var.set("Concluído.")
                messagebox.showinfo("Sucesso", f"Arquivo salvo em:\n{pasta}")
            else:
                self.status_var.set("Erro.")
                linhas = resultado.stderr.strip().splitlines()[-6:]
                messagebox.showerror(
                    "Erro no yt-dlp",
                    "\n".join(linhas) or "Falha desconhecida."
                )
        except Exception as e:
            self.status_var.set("Erro.")
            messagebox.showerror("Erro", str(e))
        finally:
            self.btn.config(state="normal")

def main():
    boot = tk.Tk()
    boot.withdraw()

    ytdlp = garantir_ytdlp()
    if not ytdlp:
        boot.destroy()
        return

    ffmpeg = garantir_ffmpeg()
    #se o usuário recusou o ffmpeg, ainda deixa continuar
    #(funciona pra vídeos que já vêm num stream único, tipo 360p/720p)
    if not ffmpeg:
        continuar = messagebox.askyesno(
            "Continuar sem ffmpeg?",
            "Sem o ffmpeg, muitas opções vão falhar:\n"
            "  • Vídeos 1080p+ (streams separados não serão juntados)\n"
            "  • Conversão pra MP3, WAV, FLAC, OPUS\n\n"
            "Continuar mesmo assim?"
        )
        if not continuar:
            boot.destroy()
            return

    boot.destroy()
    App(ytdlp, ffmpeg).mainloop()

if __name__ == "__main__":
    main()
import os
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

from yt_dlp import YoutubeDL


KV = r'''
<DownloaderUI>:
    orientation: "vertical"
    padding: dp(20)
    spacing: dp(15)

    canvas.before:
        Color:
            rgba: 0.05, 0.05, 0.07, 1
        Rectangle:
            pos: self.pos
            size: self.size

    Label:
        text: "🔥 ARNAV DOWNLOADER"
        font_size: "25sp"
        bold: True
        color: 1, 0.25, 0.1, 1
        size_hint_y: None
        height: dp(55)

    Label:
        text: "Download content you are authorized to save"
        color: 0.75, 0.75, 0.75, 1
        size_hint_y: None
        height: dp(35)

    TextInput:
        id: url_input
        hint_text: "Paste URL here..."
        multiline: False
        font_size: "17sp"
        size_hint_y: None
        height: dp(55)
        padding: dp(15)

    Button:
        text: "⬇ DOWNLOAD"
        font_size: "18sp"
        bold: True
        size_hint_y: None
        height: dp(55)
        background_normal: ""
        background_color: 1, 0.25, 0.1, 1
        on_release: root.start_download()

    ProgressBar:
        id: progress
        max: 100
        value: 0
        size_hint_y: None
        height: dp(12)

    Label:
        text: root.status
        color: 0.9, 0.9, 0.9, 1
        text_size: self.width, None
        halign: "center"

    Widget:
'''


class DownloaderUI(BoxLayout):
    status = StringProperty("Ready")

    def start_download(self):
        url = self.ids.url_input.text.strip()

        if not url:
            self.status = "❌ Please enter a URL"
            return

        self.ids.progress.value = 0
        self.status = "⏳ Starting download..."

        threading.Thread(
            target=self.download,
            args=(url,),
            daemon=True
        ).start()

    def progress_hook(self, data):
        if data["status"] == "downloading":
            total = data.get("total_bytes") or data.get("total_bytes_estimate")
            downloaded = data.get("downloaded_bytes", 0)

            if total:
                percent = downloaded * 100 / total
                Clock.schedule_once(
                    lambda dt: self.update_progress(percent)
                )

        elif data["status"] == "finished":
            Clock.schedule_once(
                lambda dt: self.set_status("🔄 Processing file...")
            )

    def update_progress(self, value):
        self.ids.progress.value = value
        self.status = f"⬇ Downloading... {value:.1f}%"

    def set_status(self, text):
        self.status = text

    def download(self, url):
        try:
            download_dir = os.path.join(
                App.get_running_app().user_data_dir,
                "downloads"
            )

            os.makedirs(download_dir, exist_ok=True)

            options = {
                "outtmpl": os.path.join(
                    download_dir,
                    "%(title)s.%(ext)s"
                ),

                "format": "bestvideo+bestaudio/best",

                "merge_output_format": "mp4",

                "noplaylist": True,

                "progress_hooks": [self.progress_hook],

                "quiet": True,

            }

            with YoutubeDL(options) as ydl:
                ydl.download([url])

            Clock.schedule_once(
                lambda dt: self.download_finished()
            )

        except Exception as e:
            message = str(e)

            Clock.schedule_once(
                lambda dt: self.download_error(message)
            )

    def download_finished(self):
        self.ids.progress.value = 100
        self.status = "✅ Download complete!"

    def download_error(self, error):
        self.status = "❌ Error: " + error[:250]


class ArnavDownloader(App):

    def build(self):
        self.title = "Arnav Downloader"
        return Builder.load_string(KV)


if __name__ == "__main__":
    ArnavDownloader().run()

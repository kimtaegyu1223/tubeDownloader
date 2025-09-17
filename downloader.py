import subprocess
from pathlib import Path
from typing import List, Optional

from pytubefix import YouTube
from utils import get_ffmpeg_path, sanitize_filename, build_format_selector, probe_audio_langs

try:
    from yt_dlp import YoutubeDL
    HAS_YTDLP = True
except Exception:
    HAS_YTDLP = False
    
# --- 상수 ---
DOWNLOAD_FOLDER = Path.home() / "Downloads" / "youtube_downloads"
PREFERRED_AUDIO_LANGS = ["ko", "en-US", "en"]  # 선호 언어 우선순위
VIDEO_TEMP_SUFFIX = ".__video.mp4"          # (표준 화질 경로에서만 사용)
AUDIO_TEMP_SUFFIX = ".__audio"              # (표준 화질 경로에서만 사용)


class Downloader:
    """
    YouTube 영상 다운로드 및 병합 로직.
    - 고화질(1080p)+언어선택: yt-dlp 사용 (ffmpeg 필요)
    - 표준 화질(프로그레시브): pytube 사용
    UI와 독립 설계, 콜백으로 진행률/로그 연동.
    """
    def __init__(self, callbacks: dict):
        self.log = callbacks.get('log', lambda _: None)
        self.update_overall_progress = callbacks.get('progress_overall', lambda _, __: None)
        self.update_current_progress = callbacks.get('progress_current', lambda _, __: None)
        self.on_complete = callbacks.get('on_complete', lambda: None)

        self.ffmpeg_path = get_ffmpeg_path()
        if not self.ffmpeg_path:
            self.log("⚠️ ffmpeg.exe를 찾을 수 없습니다. 1080p 병합이 불가하여 720p로 대체됩니다.")
        if not HAS_YTDLP:
            self.log("⚠️ yt-dlp가 설치되어 있지 않습니다. (pip install yt-dlp) — 고화질+언어 선택 기능 제한.")

    def run_downloads(self, urls: List[str], high_quality: bool):
        DOWNLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
        total_videos = len(urls)

        for idx, url in enumerate(urls, start=1):
            try:
                self._download_video(url, high_quality)
            except Exception as e:
                self.log(f"❌ '{url}' 처리 중 심각한 오류 발생: {repr(e)}")
            finally:
                self.update_overall_progress(idx, total_videos)

        self.log("✅ 모든 다운로드가 완료되었습니다.")
        self.on_complete()

    def _download_video(self, url: str, high_quality: bool):
        # 제목은 pytube로만 탐색 (신뢰성 좋음)
        yt = YouTube(url, on_progress_callback=self._progress_callback)
        safe_title = sanitize_filename(yt.title)
        self.log(f"▶️ '{safe_title}' 다운로드 시작...")

        if high_quality and self.ffmpeg_path and HAS_YTDLP:
            self._handle_high_quality_with_ytdlp(url, safe_title)
        else:
            if high_quality and (not self.ffmpeg_path or not HAS_YTDLP):
                if not self.ffmpeg_path:
                    self.log("   - ffmpeg 없음: 1080p 병합 불가 → 720p progressive로 대체합니다.")
                if not HAS_YTDLP:
                    self.log("   - yt-dlp 없음: 언어 강제 선택 불가 → 720p progressive로 대체합니다.")
            self._handle_standard_quality(yt, safe_title)

    # --- 표준 화질(프로그레시브): pytube 경로 ---
    def _handle_standard_quality(self, yt: YouTube, safe_title: str):
        stream = yt.streams.get_highest_resolution()  # 대개 720p progressive(mp4+h264+aac)
        self.log(f"   - '{safe_title}' 최고화질(Progressive) 다운로드 중...")
        self.update_current_progress(0, f"'{safe_title}' 다운로드 중... 0.0%")
        stream.download(output_path=DOWNLOAD_FOLDER, filename=f"{safe_title}.mp4")
        self.log(f"✔️ 완료: {DOWNLOAD_FOLDER / f'{safe_title}.mp4'}")

    # --- 고화질(1080p)+언어 선택: yt-dlp 경로 ---
    def _handle_high_quality_with_ytdlp(self, url: str, safe_title: str):
        # 사용 가능 오디오 언어 탐색(정보 제공용)
        langs = probe_audio_langs(url)
        if langs:
            self.log(f"   - 가용 오디오 언어: {', '.join(langs)}")
        else:
            self.log("   - 오디오 언어 메타를 확인할 수 없습니다(단일 트랙이거나 노출 제한). 선호 언어 체인으로 시도합니다.")

        fmt = build_format_selector(PREFERRED_AUDIO_LANGS, max_height=1080)
        #self.log(f"   - yt-dlp 포맷: {fmt}")

        def _hook(d):
            status = d.get("status")
            if status == "downloading":
                downloaded = d.get("downloaded_bytes", 0)
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 1
                prog = max(min(downloaded / total, 1.0), 0.0)
                self.update_current_progress(prog, f"다운로드 중... {downloaded/1e6:.1f}/{total/1e6:.1f} MB")
            elif status == "finished":
                self.update_current_progress(1.0, "병합/마무리 중...")

        ydl_opts = {
            "outtmpl": str(DOWNLOAD_FOLDER / f"{safe_title}.%(ext)s"),
            "merge_output_format": "mp4",
            "ffmpeg_location": self.ffmpeg_path,
            "prefer_ffmpeg": True,
            "format": fmt,
            "noprogress": True,
            "quiet": True,
            "progress_hooks": [_hook],
            "windowsfilenames": True, 
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.log(f"✔️ 완료: {DOWNLOAD_FOLDER / f'{safe_title}.mp4'}")
        except Exception as e:
            self.log(f"   - yt-dlp 경로 실패: {e}. 720p progressive로 폴백합니다.")
            # 폴백: 표준 화질 다운로드
            yt = YouTube(url, on_progress_callback=self._progress_callback)
            self._handle_standard_quality(yt, safe_title)

    # --- pytube 진행률 콜백(표준 화질 경로에서만 사용) ---
    def _progress_callback(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        if total_size and total_size > 0:
            bytes_downloaded = total_size - bytes_remaining
            percentage = (bytes_downloaded / total_size) * 100.0
            self.update_current_progress(percentage / 100.0, f"현재 파일 진행률: {percentage:.1f}%")

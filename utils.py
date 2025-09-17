import sys
import re
from pathlib import Path
import unicodedata
from typing import List,  Optional

    
def get_ffmpeg_path():
    """
    PyInstaller로 패키징된 경우와 일반 실행 환경 모두에서 ffmpeg.exe 경로를 찾습니다.
    없을 경우 None을 반환합니다.
    """
    try:
        # PyInstaller로 생성된 .exe 파일에서 실행될 때의 경로
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # 일반 Python 스크립트로 실행될 때의 경로
        base_path = Path(__file__).parent

    ffmpeg_exe = base_path / "ffmpeg" / "bin" / "ffmpeg.exe"
    return str(ffmpeg_exe) if ffmpeg_exe.exists() else None

def sanitize_filename(title: str) -> str:
    """
    Windows 파일명으로 사용할 수 없는 문자를 '_'로 대체합니다.
    """
    title = unicodedata.normalize("NFC", title)
    return re.sub(r'[\\/:*?"<>|]', "_", title)

# ===== 유틸 =====
def _normalize_and_sanitize(title: str) -> str:
    """한글 자모 분리(NFD) 방지: NFC로 정규화 후 사용자 정의 sanitize 적용."""
    return sanitize_filename(unicodedata.normalize("NFC", title))


# --- yt-dlp 포맷 셀렉터 생성기 ---
def build_format_selector(
    prefer_langs: List[str],
    max_height: Optional[int] = None,      # 예: 1080 → 1080p 이하
    exact_height: Optional[int] = None,    # 예: 1080 → 1080p만
    prefer_mp4_video: bool = True          # mp4(AVC) 우선
) -> str:
    """
    반환 예: "bv*[height<=1080][ext=mp4]+(ba[lang=ko][ext=m4a]/...)/best[height<=1080]"
    - exact_height가 주어지면 그 해상도만 선택
    - max_height가 주어지면 그 해상도 이하만
    - 둘 다 None이면 '가용 최고 화질' 허용
    """
    # 오디오 체인: ko m4a → ko any → en-US m4a → en-US any → en m4a → en any → bestaudio m4a → bestaudio
    audio_terms = []
    for lang in prefer_langs:
        audio_terms.append(f"ba[lang={lang}][ext=m4a]")
        audio_terms.append(f"ba[lang={lang}]")
    audio_terms += ["bestaudio[ext=m4a]", "bestaudio"]
    audio_alt = "/".join(audio_terms)

    # 비디오 조건 구성
    ext_clause = "[ext=mp4]" if prefer_mp4_video else ""
    if exact_height:
        v1 = f"bv*[height={exact_height}]{ext_clause}"
        v2 = f"bv*[height={exact_height}]"
        tail = f"best[height={exact_height}]"
    elif max_height:
        v1 = f"bv*[height<={max_height}]{ext_clause}"
        v2 = f"bv*[height<={max_height}]"
        tail = f"best[height<={max_height}]"
    else:
        # 상한 없음 = 가능한 최고 화질 허용
        v1 = f"bv*{ext_clause}"
        v2 = "bv*"
        tail = "best"

    # 우선순위: (mp4 선호) → (임의 컨테이너) → 최후 fallback
    return f"{v1}+({audio_alt})/{v2}+({audio_alt})/{tail}"


# --- yt-dlp 보조: 오디오 언어 목록 사전 탐색 ---
def probe_audio_langs(url: str) -> List[str]:
    try:
        from yt_dlp import YoutubeDL  # 선택 의존성: 없으면 빈 리스트
    except Exception:
        return []
    try:
        with YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
            info = ydl.extract_info(url, download=False)
        langs = sorted({
            f.get("language")
            for f in info.get("formats", [])
            if f.get("acodec") and f.get("acodec") != "none" and f.get("language")
        })
        return [l for l in langs if l]
    except Exception:
        return []

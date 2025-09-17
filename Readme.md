# 🎬 YouTube Downloader (Tkinter GUI)

간단한 Tkinter 기반 YouTube Downloader입니다.  
1080p 유튜브 고화질 영상을 선택하여 다운로드할 수 있습니다.

---

## 🚀 Features
- ✅ YouTube URL 입력 후 영상 다운로드
- ✅ 720p Progressive 또는 1080p 이상 고화질 다운로드 지원
- ✅ 다국어 오디오 트랙 분석하여 한국우선 적용.
- ✅ ffmpeg을 이용한 영상+오디오 병합
- ✅ PyInstaller로 빌드하여 실행 파일 빌드.

---

## 📦 Requirements

- Python **3.10+**
- [ffmpeg](https://ffmpeg.org/download.html) 설치 필요  
  - **Windows**: [Windows builds](https://www.gyan.dev/ffmpeg/builds/) → `ffmpeg.exe` 다운로드 후 프로젝트의 `ffmpeg/` 폴더에 넣기  
---

## 🛠 Installation

1. 저장소 클론
    ```bash
    git clone https://github.com/USERNAME/youtube-downloader.git
    cd youtube-downloader
    ```

2. (Windows 전용) ffmpeg 바이너리 다운로드 후 `ffmpeg/` 폴더에 넣기  

---

## ▶️ Usage

```bash
python main.py

---

## 📦 Build (Windows)

PyInstaller를 사용해 단일 실행 파일을 만들 수 있습니다.
```bash
pyinstaller --onefile --windowed --add-data "ffmpeg;ffmpeg" main.py


📂 Project Structure
youtube-downloader/
├── main.py               # 실행 진입점 (Tkinter UI)
├── downloader.py         # 다운로드 로직
├── utils.py              # 유틸 함수 (ffmpeg 경로, sanitize 등)
├── ffmpeg/               
│   └── bin/              # ffmpeg 바이너리 위치
├── requirements.txt
└── README.md
📜 License

MIT License
# 🎬 YouTube Downloader (Tkinter GUI)

간단한 Tkinter 기반 YouTube Downloader(GUI)입니다.  
1080p 유튜브 고화질 영상을 다운로드할 수 있습니다.

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
- [ffmpeg](https://www.gyan.dev/ffmpeg/builds/) ffmpeg-release-essentials.zip(v8.0) 다운로드 후 프로젝트의 `ffmpeg/` 폴더에 압축해제.
- environment.yml customtkinter==5.2.2 pyinstaller==6.16.0 등.
---

## 🛠 저장소 클론

    ```bash
    git clone https://github.com/kimtaegyu1223/tubeDownloader.git
    cd tubeDownloader
    ```

---

## ▶️ Usage

```bash
python main.py
```
---

## 📦 Build (Windows)

- PyInstaller를 사용해 단일 실행파일(exe)을 만들 수 있습니다.
```bash
pyinstaller --onefile --windowed --add-data "ffmpeg;ffmpeg" main.py
```
---

## 📂 Project Structure
```bash
tubeDownloader/
├── main.py               # 실행 진입점 (Tkinter UI)
├── downloader.py         # 다운로드 로직
├── utils.py              # 유틸 함수 (ffmpeg 경로, sanitize 등)
├── ffmpeg/               
│   └── bin/              # ffmpeg 바이너리 위치
└── README.md
```
---
## ⚠️ Disclaimer
이 프로젝트는 교육 및 개인 학습 목적으로 제작되었습니다.  
YouTube 영상 다운로드는 해당 국가의 저작권법 및 YouTube 서비스 약관을 위반할 수 있습니다.  
사용자는 본 프로젝트를 사용할 때 발생하는 모든 법적 책임을 스스로 집니다

---
## 📜 License
[MIT License](./LICENSE)

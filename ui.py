import customtkinter as ctk
import threading
from downloader import Downloader

class AppUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._create_widgets()
        self._layout_widgets()

    def _setup_ui(self):
        self.title("YouTube Downloader")
        self.geometry("1280x1000")
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

    def _create_widgets(self):
        """UI에 사용될 모든 위젯을 생성합니다."""
        # URL 입력 프레임 (스크롤 가능)
        self.url_frame = ctk.CTkScrollableFrame(self, corner_radius=12)
        self.url_entries = []
        for _ in range(3):
            self._add_url_entry_widget()

        # 옵션 및 버튼 프레임
        self.option_frame = ctk.CTkFrame(self, corner_radius=12)
        self.high_quality_var = ctk.BooleanVar(value=True)
        self.hq_check = ctk.CTkCheckBox(self.option_frame, text="고화질(1080p)",
                                        variable=self.high_quality_var, font=("", 24))
        self.add_button = ctk.CTkButton(self.option_frame, text="+ URL 추가", command=self._add_url_entry_widget,
                                        width=250, height=70, font=("", 22))
        self.download_button = ctk.CTkButton(self.option_frame, text="다운로드 시작", command=self.start_download,
                                             width=260, height=80, font=("", 24, "bold"))
        
        # 진행률 표시
        self.overall_label = ctk.CTkLabel(self, text="전체 진행률", font=("", 24, "bold"))
        self.overall_bar = ctk.CTkProgressBar(self, height=40)
        self.overall_bar.set(0)
        
        self.current_label = ctk.CTkLabel(self, text="현재 파일 진행률", font=("", 24, "bold"))
        self.current_bar = ctk.CTkProgressBar(self, height=40)
        self.current_bar.set(0)
        
        # 로그 박스
        self.logbox = ctk.CTkTextbox(self, height=400, font=("", 16), state="disabled")

    def _layout_widgets(self):
        """생성된 위젯들을 화면에 배치합니다."""
        self.url_frame.pack(pady=30, padx=30, fill="x", expand=False)
        self.option_frame.pack(pady=20, padx=30, fill="x", expand=False)
        
        self.hq_check.pack(side="left", padx=30, pady=20)
        self.add_button.pack(side="left", padx=30)
        self.download_button.pack(side="left", padx=30)
        
        self.overall_label.pack(anchor="w", padx=50, pady=(20, 5))
        self.overall_bar.pack(pady=10, padx=30, fill="x", expand=True)
        
        self.current_label.pack(anchor="w", padx=50, pady=(20, 5))
        self.current_bar.pack(pady=10, padx=30, fill="x", expand=True)
        
        self.logbox.pack(pady=30, padx=30, fill="both", expand=True)

    def _add_url_entry_widget(self):
        """URL 입력창 위젯을 생성하고 리스트에 추가합니다."""
        entry = ctk.CTkEntry(self.url_frame, placeholder_text="YouTube URL 입력",
                             width=1000, height=50, font=("", 18))
        entry.pack(pady=8, padx=20, fill="x", expand=True)
        self.url_entries.append(entry)

    def start_download(self):
        """다운로드 시작 버튼 클릭 시 호출됩니다."""
        urls = [e.get().strip() for e in self.url_entries if e.get().strip()]
        if not urls:
            self.log_message("⚠️ 최소 하나의 URL을 입력하세요.")
            return

        self.download_button.configure(state="disabled", text="다운로드 중...")
        self.logbox.configure(state="normal")
        self.logbox.delete("1.0", "end")
        self.logbox.configure(state="disabled")

        callbacks = {
            'log': self.log_message,
            'progress_overall': self.update_overall_progress,
            'progress_current': self.update_current_progress,
            'on_complete': self.on_download_complete
        }
        downloader = Downloader(callbacks)
        
        download_thread = threading.Thread(
            target=downloader.run_downloads,
            args=(urls, self.high_quality_var.get()),
            daemon=True
        )
        download_thread.start()

    # --- 콜백 메서드 (Downloader가 호출) ---
    def log_message(self, msg: str):
        """로그 메시지를 스레드에 안전하게 UI에 추가합니다."""
        def _task():
            self.logbox.configure(state="normal")
            self.logbox.insert("end", msg + "\n")
            self.logbox.see("end")
            self.logbox.configure(state="disabled")
        self.after(0, _task)

    def update_overall_progress(self, current_val: int, total_val: int):
        """전체 진행률을 스레드에 안전하게 업데이트합니다."""
        def _task():
            progress = current_val / total_val
            self.overall_bar.set(progress)
            self.overall_label.configure(text=f"전체 진행률: {current_val}/{total_val}")
        self.after(0, _task)

    def update_current_progress(self, progress: float, text: str):
        """현재 파일 진행률을 스레드에 안전하게 업데이트합니다."""
        def _task():
            self.current_bar.set(progress)
            self.current_label.configure(text=text)
        self.after(0, _task)
        
    def on_download_complete(self):
        """모든 다운로드가 완료되었을 때 호출됩니다."""
        def _task():
            self.download_button.configure(state="normal", text="다운로드 시작")
            self.update_current_progress(0, "현재 파일 진행률") # 초기화
        self.after(0, _task)
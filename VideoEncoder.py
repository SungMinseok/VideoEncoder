import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QLineEdit,
    QFileDialog, QWidget, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtCore import Qt, QThread
from datetime import datetime
import setvideo as sv
import os

class VideoEncoderThread(QThread):
    def __init__(self, input_filename, output_filename, start_sec, end_sec, bitrate="1500k"):
        super().__init__()
        self.input_filename = input_filename
        self.output_filename = output_filename
        self.start_sec = start_sec
        self.end_sec = end_sec
        self.bitrate = bitrate
        print(f"비디오 인코딩 시작: {input_filename} -> {output_filename}")
        print(f"비트레이트: {bitrate}")
        print(f"시작 시간: {start_sec}, 종료 시간: {end_sec}")


    def run(self):
        try:
            sv.compress_video2(self.input_filename, self.output_filename,
                              start_time=self.start_sec,
                              end_time=self.end_sec,
                              bitrate=self.bitrate)
        except Exception as e:
            print(e)

    def stop(self):
        self.terminate()
        self.wait()


class WindowClass(QMainWindow):
    def __init__(self):
        super().__init__()
        #self.setFixedSize(500, 205)
        self.setWindowTitle("Video Encoder")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.thread = None
        self.setup_ui()
        self.load_config()
        self.print_log("실행 가능")

    def setup_ui(self):
        
        self.setStyleSheet("""
    QWidget {
        background-color: #1a1a1a;
        color: #ffffff;
        /*border-radius: 30px;*/
        /*border: 1px solid #333333;*/
        font-family: 'Malgun Gothic', sans-serif;
        font-size: 11pt;
        font-weight: bold
                           
    }

    QLineEdit {
        background-color: #333333;
        border: 1px solid #555555;
        /*padding: 5px;*/
        /*border-radius: 5px;*/
        font-family: 'Malgun Gothic', sans-serif;
    }

    QTextEdit {
        background-color: #333333;
        border: 1px solid #555555;
        /*padding: 5px;*/
        /*border-radius: 5px;*/
        font-family: 'Malgun Gothic', sans-serif;
    }
    QPushButton {
        background-color: #444444;
        border: 1px solid #666666;
        /*padding: 5px;*/
        /*border-radius: 5px;*/
        font-family: 'Malgun Gothic', sans-serif;
    }

    QPushButton:hover {
        background-color: #555555;
    }

    QPushButton:pressed {
        background-color: #666666;
    }

    QComboBox {
        background-color: #333333;
        border: 1px solid #555555;
        /*padding: 5px;*/
        /*border-radius: 5px;*/
        font-family: 'Malgun Gothic', sans-serif;
    }

    QCheckBox {
        background-color: transparent;
        border: none;
        font-family: 'Malgun Gothic', sans-serif;
    }

    QProgressDialog {
        background-color: #1a1a1a;
        color: #ffffff;
        border-radius: 10px;
        border: 1px solid #333333;
        font-family: 'Malgun Gothic', sans-serif;
    }

    QTimeEdit {
        background-color: #333333;
        border: 1px solid #555555;
        /*padding: 5px;*/
        /*border-radius: 5px;*/
        font-family: 'Malgun Gothic', sans-serif;
    }
""")
        

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Input path
        self.input_datapath = QLineEdit()
        self.input_datapath.setPlaceholderText("Input file path")
        self.input_datapath.setAcceptDrops(True)
        self.input_datapath.dragEnterEvent = self.drag_enter_event
        self.input_datapath.dropEvent = self.drop_event

        self.btn_datapath = QPushButton("영상 선택")
        self.btn_datapath.clicked.connect(lambda: self.select_input_file(self.input_datapath))

        # Start, End, Bitrate
        self.input_startsec = QLineEdit("0")
        self.input_endsec = QLineEdit("0")
        self.input_bitrate = QLineEdit()

        # Result path
        self.input_resultpath = QLineEdit()
        self.btn_resultpath = QPushButton("저장 경로")
        self.btn_resultpath.clicked.connect(self.set_directory_path)

        # Result name
        self.input_resultname = QLineEdit()
        self.input_resultname.setPlaceholderText("출력 파일명")

        # Buttons
        self.btn_execute = QPushButton("최신 파일 실행")
        self.btn_execute_2 = QPushButton("현재 실행")
        self.btn_execute.clicked.connect(self.activate_latest)
        self.btn_execute_2.clicked.connect(self.activate)

        # Status
        self.progressLabel = QLabel()

        # Layout arrangement
        layout.addWidget(QLabel("입력 영상 경로:"))
        h1 = QHBoxLayout()
        h1.addWidget(self.input_datapath)
        h1.addWidget(self.btn_datapath)
        layout.addLayout(h1)

        layout.addWidget(QLabel("시작 / 종료 / 비트레이트:"))
        h2 = QHBoxLayout()
        h2.addWidget(self.input_startsec)
        h2.addWidget(self.input_endsec)
        h2.addWidget(self.input_bitrate)
        layout.addLayout(h2)

        layout.addWidget(QLabel("저장 경로 및 이름:"))
        h3 = QHBoxLayout()
        h3.addWidget(self.input_resultpath)
        h3.addWidget(self.btn_resultpath)
        layout.addLayout(h3)
        layout.addWidget(self.input_resultname)

                # Text Input for overlay
        self.input_overlay_text = QLineEdit()
        self.input_overlay_text.setPlaceholderText("영상에 삽입할 텍스트")
        layout.addWidget(QLabel("오버레이 텍스트:"))
        layout.addWidget(self.input_overlay_text)

        h4 = QHBoxLayout()
        h4.addWidget(self.btn_execute)
        h4.addWidget(self.btn_execute_2)
        layout.addLayout(h4)

        layout.addWidget(self.progressLabel)

        central_widget.setLayout(layout)

    def load_config(self):
        config = {}
        with open('config.txt', 'r', encoding='utf-8') as file:
            for line in file:
                key, value = line.strip().split('=')
                config[key] = value
        self.input_bitrate.setText(config.get('bitrate', '1500k'))
        self.input_resultpath.setText(config.get('save_folder', ''))

    def select_input_file(self, input_):
        data_file, _ = QFileDialog.getOpenFileName(self, "데이터 파일 선택",
                                                   directory="C:/Users/mssung/Videos/Captures",
                                                   filter="Video files (*.mp4 *.mkv)")
        if data_file:
            input_.setText(data_file)
            self.get_video_info()

    def set_directory_path(self):
        directory_path = QFileDialog.getExistingDirectory(self, "Select Directory", "")
        if directory_path:
            self.input_resultpath.setText(f'{directory_path}/')

    def drag_enter_event(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def drop_event(self, event):
        file_path = event.mimeData().urls()[0].toLocalFile()
        self.input_datapath.setText(file_path)
        self.get_video_info()

    def get_video_info(self):
        video_path = self.input_datapath.text()
        if not video_path:
            return
        video_info = sv.get_videoinfo(video_path)
        self.input_startsec.setText('0')
        self.input_endsec.setText(str(video_info.duration))

    def print_log(self, log):
        self.progressLabel.setText(log)
        QApplication.processEvents()

    def activate_latest(self):
        self.input_datapath.setText(self.set_most_recent_file('C:/Users/mssung/Videos/Captures/'))
        self.get_video_info()
        self.encode_video()

    def activate(self):
        self.encode_video()

    def encode_video(self):
        input_filename = self.input_datapath.text()
        output_path = self.input_resultpath.text()
        start_sec = float(self.input_startsec.text())
        end_sec = float(self.input_endsec.text())
        tempname = self.input_resultname.text().strip()
        if not tempname:
            tempname = datetime.now().strftime('%y%m%d_%H%M')
            self.input_resultname.setText(tempname)

        output_filename = f'{output_path}{tempname}.mp4'

        if self.thread and self.thread.isRunning():
            self.thread.stop()

        self.thread = VideoEncoderThread(input_filename, output_filename, start_sec, end_sec, self.input_bitrate.text())
        self.thread.finished.connect(self.on_thread_finished)
        self.thread.start()

    def set_most_recent_file(self, folder_path):
        try:
            files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            if not files:
                print("No files found.")
                return None
            most_recent_file = max(files, key=lambda f: os.path.getmtime(os.path.join(folder_path, f)))
            return os.path.join(folder_path, most_recent_file)
        except Exception as e:
            print("Error:", e)
            return None

    def on_thread_finished(self):
        print("Thread finished")
        os.startfile(self.input_resultpath.text())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WindowClass()
    window.show()
    sys.exit(app.exec_())

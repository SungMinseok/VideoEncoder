import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QLineEdit,
    QFileDialog, QWidget, QVBoxLayout, QHBoxLayout, QComboBox
)
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QColor, QPixmap, QIcon
from datetime import datetime
import setvideo as sv
import os
import subprocess
import re

class VideoEncoderThread(QThread):
    def __init__(self, input_filename, output_filename, start_sec, end_sec, bitrate="1500k",overlay_entries=[], style_str=""):
        super().__init__()
        self.input_filename = input_filename
        self.output_filename = output_filename
        self.start_sec = start_sec
        self.end_sec = end_sec
        self.bitrate = bitrate
        #self.overlay_text = overlay_text
        self.overlay_entries = overlay_entries
        self.style_str = style_str

        print(f"비디오 인코딩 시작: {input_filename} -> {output_filename}")
        print(f"비트레이트: {bitrate}")
        print(f"시작 시간: {start_sec}, 종료 시간: {end_sec}")


    def run(self):
        try:
            overlays = self.overlay_entries  # 생성자에서 넘겨받은 리스트
            sv.compress_video3_with_segments(
                self.input_filename, self.output_filename,
                overlays=overlays,
                start_time=self.start_sec,
                end_time=self.end_sec,
                bitrate=self.bitrate,
                style_str=self.style_str

            )
            # sv.compress_video2_with_text(self.input_filename, self.output_filename,
            #                   start_time=self.start_sec,
            #                   end_time=self.end_sec,
            #                   bitrate=self.bitrate,
            #                   text=self.overlay_text
            #                   )
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

        self.btn_refreshDatapath = QPushButton("🔃F5")
        self.btn_refreshDatapath.setShortcut("F5")
        #self.btn_refreshDatapath.clicked.connect(lambda: self.set_most_recent_file('C:/Users/mssung/Videos/Captures/'))
        self.btn_refreshDatapath.clicked.connect(self.refreshDatapath)

        self.btn_datapath = QPushButton("영상 선택")
        self.btn_datapath.clicked.connect(lambda: (self.select_input_file(self.input_datapath),self.get_video_info()))

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
        self.btn_execute = QPushButton("최신 파일 실행 F2")
        self.btn_execute.setShortcut("F2")
        self.btn_execute.setStyleSheet("background-color: blue; color: #ffffff;")
        self.btn_execute_2 = QPushButton("현재 실행 F3")
        self.btn_execute_2.setShortcut("F3")
        self.btn_execute_2.setStyleSheet("background-color: #444444; color: #ffffff;")
        self.btn_execute.clicked.connect(self.activate_latest)
        self.btn_execute_2.clicked.connect(self.activate)

        # Status
        self.progressLabel = QLabel()

        # Layout arrangement
        layout.addWidget(QLabel("입력 영상 경로:"))
        h1 = QHBoxLayout()
        h1.addWidget(self.input_datapath)
        h1.addWidget(self.btn_refreshDatapath)
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
        # self.input_overlay_text = QLineEdit()
        # self.input_overlay_text.setPlaceholderText("영상에 삽입할 텍스트")
        # layout.addWidget(QLabel("오버레이 텍스트:"))
        # layout.addWidget(self.input_overlay_text)

        layout.addWidget(QLabel("자막 스타일 옵션:"))
        style_row = QHBoxLayout()

        self.combo_color = QComboBox()
        self.combo_color.addItems([
            "white", "black", "gray", "silver", "red", "maroon", "yellow", "olive",
            "lime", "green", "aqua", "teal", "blue", "navy", "fuchsia", "purple",
            "orange", "gold", "pink", "brown", "cyan", "magenta", "lightblue",
            "lightgreen", "lightgray", "darkblue", "darkred", "darkgreen"
        ])
        self.combo_color.setCurrentText("white")

        self.combo_size = QComboBox()
        self.combo_size.addItems(["24", "32", "40", "70"])
        self.combo_size.setCurrentText("32")

        self.combo_position = QComboBox()
        self.combo_position.addItems(["하단", "상단"])
        self.combo_position.setCurrentText("하단")

        style_row.addWidget(QLabel("색상:"))
        style_row.addWidget(self.combo_color)
        style_row.addWidget(QLabel("크기:"))
        style_row.addWidget(self.combo_size)
        style_row.addWidget(QLabel("위치:"))
        style_row.addWidget(self.combo_position)

        layout.addLayout(style_row)
        # --- 추가 자막 스타일 옵션 (border, boxcolor) ---
        extra_style_row = QHBoxLayout()

        # Border Width
        self.combo_borderw = QComboBox()
        self.combo_borderw.addItems(["0", "1", "2", "3", "4", "5"])
        self.combo_borderw.setCurrentText("1")

        # Border Color
        self.combo_bordercolor = QComboBox()
        self.combo_bordercolor.addItems(["black", "white", "red", "blue", "yellow", "green"])
        self.combo_bordercolor.setCurrentText("black")

        # Box Color (optional background box)
        self.combo_boxcolor = QComboBox()
        self.combo_boxcolor.addItems(["transparent", "black@0.3", "black@0.5", "black@0.8", "white@0.5", "yellow@0.5"])
        self.combo_boxcolor.setCurrentText("transparent")

        extra_style_row.addWidget(QLabel("외곽선 굵기:"))
        extra_style_row.addWidget(self.combo_borderw)
        extra_style_row.addWidget(QLabel("외곽선 색상:"))
        extra_style_row.addWidget(self.combo_bordercolor)
        extra_style_row.addWidget(QLabel("박스 색상:"))
        extra_style_row.addWidget(self.combo_boxcolor)

        layout.addLayout(extra_style_row)






        # --- Overlay Text Section ---

        layout.addWidget(QLabel("자막 구간 설정:"))
        self.btn_add_overlay = QPushButton("자막 구간 추가")
        self.btn_add_overlay.clicked.connect(self.add_overlay_row)
        layout.addWidget(self.btn_add_overlay)
        self.overlay_list = QVBoxLayout()
        # --- Overlay Text Section ---


        layout.addLayout(self.overlay_list)
        layout.addStretch()
        # --- End of Overlay Text Section ---


        h4 = QHBoxLayout()
        h4.addWidget(self.btn_execute)
        h4.addWidget(self.btn_execute_2)

        self.btn_make_gif = QPushButton("GIF 만들기")
        self.btn_make_gif.clicked.connect(self.make_gif)

        h4.addWidget(self.btn_make_gif)
        layout.addLayout(h4)

        layout.addWidget(self.progressLabel)

        central_widget.setLayout(layout)

        self.setup_color_dropdown()

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
        
        current_time = datetime.now().strftime('%y%m%d_%H%M')
        self.input_resultname.setText(current_time)#press Q → double detail popups
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
        #text = self.input_overlay_text.text().strip()
        overlays = self.get_overlay_entries()

        if self.thread and self.thread.isRunning():
            self.thread.stop()

        style_str = self.get_drawtext_style()

        self.thread = VideoEncoderThread(input_filename, output_filename, start_sec, end_sec, self.input_bitrate.text(), overlays, style_str)
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
        
    def add_overlay_row(self):
        row_layout = QHBoxLayout()
        start_input = QLineEdit()
        start_input.setPlaceholderText("시작")
        end_input = QLineEdit()
        end_input.setPlaceholderText("종료")
        text_input = QLineEdit()
        text_input.setPlaceholderText("표시할 텍스트")
        remove_btn = QPushButton("❌")
        remove_btn.setFixedWidth(30)

        row_layout.addWidget(start_input)
        row_layout.addWidget(end_input)
        row_layout.addWidget(text_input)
        row_layout.addWidget(remove_btn)

        def remove_row():
            for i in reversed(range(row_layout.count())):
                widget = row_layout.itemAt(i).widget()
                row_layout.removeWidget(widget)
                widget.deleteLater()
            self.overlay_list.removeItem(row_layout)

        remove_btn.clicked.connect(remove_row)
        self.overlay_list.addLayout(row_layout)

    def get_overlay_entries(self):
        overlays = [] #자막 한줄 한줄줄
        for i in range(self.overlay_list.count()):
            row_layout = self.overlay_list.itemAt(i)
            start = row_layout.itemAt(0).widget().text()
            end = row_layout.itemAt(1).widget().text()
            text = row_layout.itemAt(2).widget().text()
            if start and end and text:
                overlays.append({
                    "start": float(start),
                    "end": float(end),
                    "text": text
                })
        return overlays
    
    # def get_drawtext_style(self):
    #     font_path = "C\\:/Windows/Fonts/malgun.ttf"
    #     color = self.combo_color.currentText()
    #     size = self.combo_size.currentText()
    #     position = self.combo_position.currentText()

    #     y_pos = "h-line_h-10" if position == "하단" else "10"

    #     return (
    #         #f"fontfile={font_path}:"
    #         f"fontcolor={color}:fontsize={size}:borderw=1:"
    #         f"x=(w-text_w)/2:y={y_pos}"
    #     )
    
    def get_drawtext_style(self):
        font_path = "C\\:/Windows/Fonts/malgun.ttf"

        color = self.combo_color.currentText()
        size = self.combo_size.currentText()
        position = self.combo_position.currentText()
        borderw = self.combo_borderw.currentText()
        bordercolor = self.combo_bordercolor.currentText()
        boxcolor = self.combo_boxcolor.currentText()

        y_pos = "h-line_h-10" if position == "하단" else "10"

        style = (
            #f"fontfile={font_path}:"
            f"fontcolor={color}:fontsize={size}:"
            f"borderw={borderw}:bordercolor={bordercolor}:"
            f"x=(w-text_w)/2:y={y_pos}"
        )

        # 박스 색상 적용
        if boxcolor != "transparent":
            style += f":box=1:boxcolor={boxcolor}"

        return style


    def setup_color_dropdown(self):
        self.combo_color.clear()
        color_names = [
            "white", "black", "gray", "silver", "red", "maroon", "yellow", "olive",
            "lime", "green", "aqua", "teal", "blue", "navy", "fuchsia", "purple",
            "orange", "gold", "pink", "brown", "cyan", "magenta", "lightblue",
            "lightgreen", "lightgray", "darkblue", "darkred", "darkgreen"
        ]

        for color_name in color_names:
            pixmap = QPixmap(20, 20)
            pixmap.fill(QColor(color_name))
            icon = QIcon(pixmap)
            self.combo_color.addItem(icon, color_name)

    def refreshDatapath(self):
        self.input_datapath.setText(self.set_most_recent_file('C:/Users/mssung/Videos/Captures/'))
        self.get_video_info()
        self.input_resultname.setText(datetime.now().strftime('%y%m%d_%H%M'))

    def make_gif(self):
        input_filename = self.input_datapath.text()
        start_sec = float(self.input_startsec.text())
        end_sec = float(self.input_endsec.text())
        output_path = self.input_resultpath.text()
        tempname = self.input_resultname.text().strip()

        if not tempname:
            tempname = datetime.now().strftime('%y%m%d_%H%M')
            self.input_resultname.setText(tempname)

        output_filename = f"{output_path}{tempname}.gif"
        duration = end_sec - start_sec

        cmd = [
            "ffmpeg",
            "-y",
            "-ss", str(start_sec),
            "-t", str(duration),
            "-i", input_filename,
            "-vf", "fps=10,scale=480:-1:flags=lanczos",
            "-loop", "0",
            output_filename
        ]

        print("실행 명령어:", " ".join(cmd))
        subprocess.run(cmd, shell=True)
        self.print_log(f"GIF 생성 완료: {output_filename}")



    def on_thread_finished(self):
        print("Thread finished")
        os.startfile(self.input_resultpath.text())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WindowClass()
    window.show()
    sys.exit(app.exec_())

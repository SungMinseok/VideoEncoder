import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QPixmap
import setvideo as sv
import os
from PyQt5.QtWidgets import QTreeWidgetItem
from datetime import datetime


form_class = uic.loadUiType('VideoEncoder_UI.ui')[0]

class VideoEncoderThread(QThread):
    def __init__(self, input_filename, output_filename, start_sec, end_sec, bitrate="1500k"):
        super().__init__()
        self.input_filename = input_filename
        self.output_filename = output_filename
        self.start_sec = start_sec
        self.end_sec = end_sec
        self.bitrate = bitrate

    def run(self):
        try:
            sv.compress_video(self.input_filename, self.output_filename, start_time=self.start_sec, end_time=self.end_sec, bitrate=self.bitrate)
            #sv.add_text_to_video(self.output_filename, 'rev.33043', self.output_filename)
        except Exception as e:
            print(e)

    def stop(self):
        self.terminate()
        self.wait()

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(500, 205)
        self.print_log("실행 가능")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        config = {}
        with open('config.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        for line in lines:
            line = line.strip()
            key, value = line.split('=')
            config[key] = value

        self.input_startsec.setText("0")
        self.input_endsec.setText("0")
        self.input_bitrate.setText(config['bitrate'])
        self.input_resultpath.setText(config['save_folder'])

        self.btn_datapath.clicked.connect(lambda: self.select_input_file(self.input_datapath))
        self.input_datapath.setAcceptDrops(True)
        self.input_datapath.dragEnterEvent = self.drag_enter_event
        self.input_datapath.dropEvent = self.drop_event

        # self.btn_datapath_2.clicked.connect(lambda: self.select_input_file(self.input_datapath_2))
        # self.input_datapath_2.setAcceptDrops(True)
        # self.input_datapath_2.dragEnterEvent = self.drag_enter_event
        # self.input_datapath_2.dropEvent = self.drop_event

        self.btn_resultpath.clicked.connect(self.set_directory_path)
        self.btn_execute.clicked.connect(self.activate)
        self.btn_execute_2.clicked.connect(self.merge)

        # Add an attribute to keep track of the thread
        self.thread = None


    def select_input_file(self, input_):
        file_filter = "Video files (*.mp4 *.mkv)"
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        data_file, _ = QFileDialog.getOpenFileName(self, "데이터 파일 선택", directory="C:/Users/mssung/Videos/Captures", filter=file_filter, options=options)
        try:
            self.input_datapath.setText(data_file)
            self.get_video_info()
        except: 
            pass

    def set_directory_path(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        directory_path = QFileDialog.getExistingDirectory(self, "Select Directory", "", options=options)
        if directory_path:
            self.input_resultpath.setText(f'{directory_path}/')

    def drag_enter_event(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def drop_event(self, event):
        urls = event.mimeData().urls()
        file_path = urls[0].toLocalFile()
        self.input_datapath.setText(file_path)
        self.get_video_info()

    def get_video_info(self):
        video_path = self.input_datapath.text()
        if video_path == "":
            return
        video_info = sv.get_videoinfo(video_path)
        self.input_startsec.setText('0')
        self.input_endsec.setText(str(video_info.duration))

    def print_log(self, log):
        self.progressLabel.setText(log)
        QApplication.processEvents()

    def activate(self):

#
        self.input_datapath.setText(self.set_most_recent_file(fr'C:/Users/mssung/Videos/Captures/'))
        self.get_video_info()


        input_filename = self.input_datapath.text()
        output_path = self.input_resultpath.text()
        start_sec = float(self.input_startsec.text())
        end_sec = float(self.input_endsec.text())
        tempname = self.input_resultname.text()


        
        if tempname == "":
            tempname = "result"

        current_time = datetime.now().strftime('%y%m%d_%H%M')
        self.input_resultname.setText(current_time)

        # Create the output filename in 'yymmdd_hhmm.mp4' format
        output_filename = f'{output_path}{current_time}.mp4'
        #output_filename = f'{output_path}{tempname}.mp4'

        # Stop the previous thread if it is still running
        if self.thread is not None and self.thread.isRunning():
            self.thread.stop()

        self.thread = VideoEncoderThread(input_filename, output_filename, start_sec, end_sec)
        self.thread.finished.connect(self.on_thread_finished)
        self.thread.start()


    def set_most_recent_file(self,folder_path):
        try:
            # Get all files in the directory
            files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            
            # Check if folder is empty
            if not files:
                print("No files found in the specified folder.")
                return None
            
            # Get the most recent file based on modification time
            most_recent_file = max(files, key=lambda f: os.path.getmtime(os.path.join(folder_path, f)))
            input_filename = os.path.join(folder_path, most_recent_file)
            print(f"Most recent file: {input_filename}")
            return input_filename
        except Exception as e:
            print(f"Error while fetching the most recent file: {e}")
            return None
        
    def merge(self):
        video_0 = self.input_datapath.text()
        video_1 = self.input_datapath_2.text()
        result_dir = self.input_resultpath.text()
        tempname = self.input_resultname.text()
        if tempname == "":
            tempname = "result"
        output_filename = f'{result_dir}{tempname}.mp4'
        #merge_videos(video_0, video_1, output_filename)

    def on_thread_finished(self):
        print("Thread finished")
        # Additional cleanup if needed
        output_path = self.input_resultpath.text()
        os.startfile(output_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()

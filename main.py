from utils import initialize, save_conf, is_valid_path
from ppt_maker import make_ppt
import os
import time

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog,
    QMessageBox, QFrame, QStatusBar,
    QProgressBar)
from PySide6.QtGui import QIcon, QPixmap, QPalette, QColor
from functools import partial

class MyWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.conf = initialize()

        #아이콘 설정
        self.icon_path = "./data/favicon.ico"
        self.setWindowIcon(QIcon(self.icon_path))
        #제목 설정
        self.setWindowTitle("필드 구축 분석 프로그램")
        #크기 설정
        self.setGeometry(100, 100, 400, 400)

        #status bar 설정
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 색상 설정
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(192, 192, 192))
        self.setPalette(palette)

        #메인
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # 엔지니어 이름 설정
        row_layout = QHBoxLayout()
        label = QLabel("엔지니어", self)
        eng_input = QLineEdit(self)
        eng_input.setText(self.conf['engineer'])
        callback = partial(self.on_text_changed, name='engineer')
        eng_input.textChanged.connect(callback)
        eng_input.returnPressed.connect(self.update_conf)
        row_layout.addWidget(label)
        row_layout.addWidget(eng_input)
        main_layout.addLayout(row_layout)

        # 사이트명 설정
        row_layout = QHBoxLayout()
        label = QLabel("사이트명", self)
        site_input = QLineEdit(self)
        site_input.setText(self.conf['site'])
        callback = partial(self.on_text_changed, name='site')
        site_input.textChanged.connect(callback)
        site_input.returnPressed.connect(self.update_conf)
        row_layout.addWidget(label)
        row_layout.addWidget(site_input)
        main_layout.addLayout(row_layout)

        # 설치일자 설정
        row_layout = QHBoxLayout()
        label = QLabel("설치일자", self)
        date_input = QLineEdit(self)
        date_input.setText(self.conf['date'])
        callback = partial(self.on_text_changed, name='date')
        date_input.textChanged.connect(callback)
        date_input.returnPressed.connect(self.update_conf)
        row_layout.addWidget(label)
        row_layout.addWidget(date_input)
        main_layout.addLayout(row_layout)

        # 구분자
        separator = QFrame(self)
        separator.setFrameShape(QFrame.HLine)
        main_layout.addWidget(separator)
        
        # 모터 이름, 파일 설정
        for i in range(10):
            mName = self.conf['motor_set'][i]['name']
            row_layout = QHBoxLayout()
            label = QLabel(f"모터{i+1:3.0f}\t", self)
            mName_input = QLineEdit(self)
            if mName == "":
                mName_input.setPlaceholderText("모터명 입력")
                f_select_msg = f""
            else:
                mName_input.setText(mName)
                f_select_msg = f"{len(self.conf['motor_set'][i]['data'])} files"
            callback = partial(self.on_motorName_changed, motor_index=i)
            mName_input.textChanged.connect(callback)
            mName_input.returnPressed.connect(self.update_conf)
            mList_button = QPushButton("AWS 파일 선택", self)
            flist_label = QLabel(f_select_msg, self)
            callback = partial(self.select_aws_files, motor_index=i, qlabel=flist_label)
            mList_button.clicked.connect(callback)
            row_layout.addWidget(label)
            row_layout.addWidget(mName_input)
            row_layout.addWidget(mList_button)
            row_layout.addWidget(flist_label)
            main_layout.addLayout(row_layout)
        

        # 구분자
        separator = QFrame(self)
        separator.setFrameShape(QFrame.HLine)
        main_layout.addWidget(separator)

        #결과파일 폴더 설정
        row_layout = QHBoxLayout()
        label = QLabel("결과파일 폴더 경로", self)
        path_input = QLineEdit(self)
        path_input.setText(os.path.dirname(__file__))
        row_layout.addWidget(label)
        row_layout.addWidget(path_input)
        main_layout.addLayout(row_layout)
        self.path_input = path_input

        #실행 버튼
        result_button = QPushButton("결과 생성", self)
        result_button.clicked.connect(self.generate_result)
        main_layout.addWidget(result_button)
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)
        
    def on_text_changed(self, text, name):
        self.conf[name] = text

    def on_motorName_changed(self, text, motor_index):
        self.conf['motor_set'][motor_index]['name'] = text

    def select_aws_files(self, motor_index, qlabel:QLabel):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        files, _ = QFileDialog.getOpenFileNames(self, "AWS JSON 파일 선택", "", "JSON 파일 (*.json)", options=options)
        
        if not files:  # 파일을 선택하지 않거나 다이얼로그를 종료한 경우
            self.conf['motor_set'][motor_index]['data'] = []
            qlabel.setText('0 files')
        else:
            self.conf['motor_set'][motor_index]['data'] = files
            qlabel.setText(f'{len(files)} files')
        
        self.update_conf()

    def update_conf(self):
        save_conf(self.conf)
        self.status_bar.showMessage("설정정보가 저장되었습니다.")

    def generate_result(self):
        dir_path = self.path_input.text()
        if is_valid_path(dir_path):
            self.progress_bar.show()
                
            self.conf['result_dir'] = dir_path
            self.update_conf()
            self.status_bar.showMessage("결과 리포트를 생성중입니다.")
            result_path = make_ppt(conf=self.conf, save_dir=dir_path, 
                                   progressbar=self.progress_bar,
                                   statusbar = self.status_bar)
            
            self.progress_bar.hide()

            popup = QMessageBox()
            popup.setWindowTitle("생성 완료!")
            popup.setText(f"파일 생성 완료!: {result_path}")
            popup.setWindowIcon(QIcon(self.icon_path))
            popup.setIconPixmap(QPixmap(self.icon_path))
            popup.exec()
        else:
            popup = QMessageBox()
            popup.setWindowTitle("경로 에러")
            popup.setText("유효하지 않은 경로입니다. 올바른 폴더 경로를 설정하세요..")
            popup.setWindowIcon(QIcon(self.icon_path))
            popup.setIconPixmap(QPixmap(self.icon_path))
            popup.exec()
            self.status_bar.showMessage("")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())

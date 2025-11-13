import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QFileDialog, QLabel, QComboBox, QProgressBar, QMessageBox
)
from compressor import GPUCompressor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GPU File Compressor (nvCOMP)")
        self.resize(400, 250)

        # Widgets
        self.label = QLabel("Select a file to compress or decompress")
        self.progress = QProgressBar()
        self.progress.setValue(0)

        self.select_btn = QPushButton("Select File")
        self.compress_btn = QPushButton("Compress")
        self.decompress_btn = QPushButton("Decompress")
        self.compress_btn.setEnabled(False)
        self.decompress_btn.setEnabled(False)

        self.algorithm = QComboBox()
        self.algorithm.addItems(["LZ4", "Bitcomp", "Deflate", "Zstd", "GDeflate", "Snappy", "Cascaded", "ANS"])

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.algorithm)
        layout.addWidget(self.progress)
        layout.addWidget(self.select_btn)
        layout.addWidget(self.compress_btn)
        layout.addWidget(self.decompress_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Signals
        self.select_btn.clicked.connect(self.select_file)
        self.compress_btn.clicked.connect(lambda: self.run_task("compress"))
        self.decompress_btn.clicked.connect(lambda: self.run_task("decompress"))

        self.input_path = None
        self.worker = None

    def select_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select file")
        if file:
            self.input_path = file
            self.label.setText(f"Selected: {file}")
            self.compress_btn.setEnabled(True)
            self.decompress_btn.setEnabled(True)

    def run_task(self, mode):
        if not self.input_path:
            return

        algo = self.algorithm.currentText()
        suffix = ".gpzip" if mode == "compress" else ".out"
        output_path = self.input_path + suffix

        self.progress.setValue(0)
        self.compress_btn.setEnabled(False)
        self.decompress_btn.setEnabled(False)

        self.worker = GPUCompressor(self.input_path, output_path, algorithm=algo, mode=mode)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, success, message):
        self.compress_btn.setEnabled(True)
        self.decompress_btn.setEnabled(True)
        if success:
            QMessageBox.information(self, "Done", f"Operation complete:\n{message}")
        else:
            QMessageBox.critical(self, "Error", f"Failed:\n{message}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

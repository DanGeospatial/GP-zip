"""

Run the UI using PySide6 and make calls to compression/decompression

Copyright 2025 Daniel Nelson

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QFileDialog, QLabel, QComboBox, QProgressBar, QMessageBox
)
from compressor import GPUCompressor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Config window
        self.setWindowTitle("GPU File Compressor (nvCOMP)")
        self.resize(400, 250)

        # Progress Bar Widget
        self.label = QLabel("Select a file to compress or decompress")
        self.progress = QProgressBar()
        self.progress.setValue(0)

        # Button Widgets
        self.select_btn = QPushButton("Select File")
        self.compress_btn = QPushButton("Compress")
        self.decompress_btn = QPushButton("Decompress")
        # Turn on buttons once file selected
        self.compress_btn.setEnabled(False)
        self.decompress_btn.setEnabled(False)

        # Combo Widget
        self.algorithm = QComboBox()
        # These must be only the supported by cu12
        self.algorithm.addItems(["ANS", "Bitcomp", "Cascaded", "Deflate", "GDeflate", "LZ4", "Snappy", "Zstd"])

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

        # Vars
        self.input_path = None
        self.worker = None

    def select_file(self):
        # Get file path and then enable buttons
        file, _ = QFileDialog.getOpenFileName(self, "Select file")
        if file:
            self.input_path = file
            self.label.setText(f"Selected: {file}")
            self.compress_btn.setEnabled(True)
            self.decompress_btn.setEnabled(True)

    def run_task(self, mode):
        # Check for path
        if not self.input_path:
            return

        # Set algo and file prefix
        algo = self.algorithm.currentText()
        suffix = ".gpzip" if mode == "compress" else ".out"
        output_path = self.input_path + suffix

        # Turn off buttons
        self.progress.setValue(0)
        self.compress_btn.setEnabled(False)
        self.decompress_btn.setEnabled(False)

        self.worker = GPUCompressor(self.input_path, output_path, algorithm=algo, mode=mode)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, success, message):
        # Turn back on buttons
        self.compress_btn.setEnabled(True)
        self.decompress_btn.setEnabled(True)
        # Display error or success messages
        if success:
            QMessageBox.information(self, "Done", f"Operation complete:\n{message}")
        else:
            QMessageBox.critical(self, "Error", f"Failed:\n{message}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

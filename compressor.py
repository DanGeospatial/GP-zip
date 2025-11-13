import os
import numpy as np
from nvidia import nvcomp
from PySide6.QtCore import QThread, Signal

CHUNK_SIZE = 64 * 1024 * 1024  # 64MB chunks (adjust for your GPU memory)


class GPUCompressor(QThread):
    progress = Signal(int)
    finished = Signal(bool, str)

    def __init__(self, input_path, output_path, algorithm="LZ4", mode="compress"):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.algorithm = algorithm
        self.mode = mode

    def run(self):
        try:
            codec = nvcomp.Codec(algorithm=self.algorithm, device_id=0)
            file_size = os.path.getsize(self.input_path)
            processed = 0

            with open(self.input_path, "rb") as fin, open(self.output_path, "wb") as fout:
                while True:
                    chunk = fin.read(CHUNK_SIZE)
                    if not chunk:
                        break

                    arr_h = nvcomp.as_array(np.frombuffer(chunk, dtype=np.uint8))
                    arr_d = arr_h.cuda()

                    if self.mode == "compress":
                        result = codec.encode(arr_d)
                    else:
                        result = codec.decode(arr_d)

                    out_bytes = bytes(result.cpu())
                    fout.write(out_bytes)

                    processed += len(chunk)
                    percent = int(100 * processed / file_size)
                    self.progress.emit(percent)

            self.finished.emit(True, self.output_path)

        except Exception as e:
            print("Error:", e)
            self.finished.emit(False, str(e))

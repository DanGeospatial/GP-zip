import os
import sys
import struct
from nvidia import nvcomp
from PySide6.QtCore import QThread, Signal

CHUNK_SIZE = 256 * 1024 * 1024  # 256MB chunks (adjust for your GPU memory)


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
            file_size = os.path.getsize(self.input_path)
            processed = 0

            if self.mode == "compress":
                codec = nvcomp.Codec(algorithm=self.algorithm)

                with open(self.input_path, 'rb') as fin, open(self.output_path, 'wb') as fout:
                    # Optional magic header so we can recognise the file later
                    fout.write(b'NVCOMP')
                    while True:
                        data = fin.read(CHUNK_SIZE)
                        if not data:  # EOF
                            break

                        # Zero‑copy host array that references the bytes buffer
                        src_h = nvcomp.as_array(data)
                        src_d = src_h.cuda()  # copy to nvidia device

                        # Compress nvcomp.Array that contains the NVCOMP_NATIVE header
                        comp_arr = codec.encode(src_d)

                        # Pull the compressed data back to CPU
                        comp_bytes = bytes(comp_arr.cpu())

                        # Write a minimal 8‑byte record: 4 for input size, 4 for compressed size
                        fout.write(struct.pack('<II', len(data), len(comp_bytes)))
                        fout.write(comp_bytes)

                        processed += len(data)
                        percent = int(100 * processed / file_size)
                        self.progress.emit(percent)

            else:
                codec = nvcomp.Codec()

                with open(self.input_path, 'rb') as fin, open(self.output_path, 'wb') as fout:
                    # skip magic header if present
                    magic = fin.read(6)
                    if magic != b'NVCOMP':
                        fin.seek(0)  # no magic – rewind

                    while True:
                        header = fin.read(8)  # input size, compressed size
                        if not header:  # EOF
                            break
                        src_len, dst_len = struct.unpack('<II', header)
                        comp_bytes = fin.read(dst_len)

                        # Convert compressed bytes to a zero‑copy host array
                        comp_h = nvcomp.as_array(comp_bytes)
                        comp_d = comp_h.cuda()

                        # Decode nvcomp.Array with the original bytes
                        dec_arr = codec.decode(comp_d)

                        # Back to CPU and trim to the exact original size
                        dec_bytes = bytes(dec_arr.cpu())[:src_len]
                        fout.write(dec_bytes)

                        processed += (len(comp_bytes) + sys.getsizeof(header))
                        percent = int(100 * processed / file_size)
                        self.progress.emit(percent)

            self.finished.emit(True, self.output_path)

        except Exception as e:
            print("Error:", e)
            self.finished.emit(False, str(e))

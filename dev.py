import struct
from nvidia import nvcomp

file_in = "D:/dNBR_total_3m.csv"
file_out = "D:/dNBR_total_3m_out.csv.gpzip"

file_in_dc = "D:/dNBR_total_3m_out.csv.gpzip"
file_out_dc = "D:/dNBR_total_3m_out.csv"
"""
mode = "compress"
# mode = "decomp"

with open(file_in, "rb") as fin, open(file_out, "wb") as fout:
    chunk = fin.read()
    arr_h = nvcomp.as_array(chunk)
    arr_d = arr_h.cuda()

    if mode == "compress":
        codec = nvcomp.Codec(algorithm="LZ4")
        result = codec.encode(arr_d)
    else:
        codec = nvcomp.Codec()
        result = codec.decode(arr_d)

    out_bytes = bytes(result.cpu())
    fout.write(out_bytes)
"""

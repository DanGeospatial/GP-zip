# GP-zip
ZIP files but with your Nvidia GPU! 
Originally designed for compressing research data for archiving. 

# Requirements 
- PySide6>=6.6
- nvidia-nvcomp-cu12>=3.0.6
- numpy

# To Add:
- Decompression automatically picks the correct codec
- Streaming progress (based on GPU kernel completion events)
- Multithreaded chunk compression
- Multi-GPU compression

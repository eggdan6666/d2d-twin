from pathlib import Path
from pypdf import PdfReader
for name,path in [('ad','corpus/data/raw_pdf/ADI/ad5592r.pdf'),('lis','corpus/data/raw_pdf/ST/LIS3DH.pdf')]:
 out=Path('_setup/ir_drafts')/f'{name}_pages.txt'; r=PdfReader(path)
 with out.open('w',encoding='utf-8') as f:
  for i,p in enumerate(r.pages):
   f.write(f'===== PDF PAGE {i+1} =====\n'); f.write((p.extract_text() or '')+'\n')
 print(out)

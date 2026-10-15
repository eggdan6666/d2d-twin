from pathlib import Path
text=Path('_setup/ir_drafts/lis_pages.txt').read_text(encoding='utf-8')
parts=text.split('===== PDF PAGE ')
for n in [24,25,26,27,28,29,30,31,33,34,35,36,37,38,39,40]:
 for x in parts:
  if x.startswith(str(n)+' ====='):
   print('\n===== PAGE',n,'====='); print(x[:6000]); break

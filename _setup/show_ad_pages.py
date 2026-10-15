from pathlib import Path
text=Path('_setup/ir_drafts/ad_pages.txt').read_text(encoding='utf-8')
parts=text.split('===== PDF PAGE ')
for n in range(35,53):
 for x in parts:
  if x.startswith(str(n)+' ====='):
   print('\n===== PAGE',n,'====='); print(x[:7000]); break

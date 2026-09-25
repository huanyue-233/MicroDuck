from pathlib import Path
p=Path(r'C:\Users\Administrator\Desktop\MicroDuck\report')
for f in [p/'outline.md',p/'deck_spec.json',p/'speech.md',*sorted((p/'prompts').glob('slide_*.json'))]:
 s=f.read_text(encoding='utf-8')
 print(f.name, 'question_marks',s.count('?'),'replacement_chars',s.count('\ufffd'),'cjk',sum('\u4e00'<=c<='\u9fff' for c in s))

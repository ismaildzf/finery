import re

s = open('_design/_dragon_page.html', encoding='utf-8', errors='ignore').read()
for vid in ['4ced6e30714dddf69119ef7b7ec666ec', 'b5cc4d4cf6df40655897d117a0f39927', 'c6b33b279980631a18cb3dcb3530e24d', '7009700']:
    i = s.find(vid)
    print('=====', vid, i)
    if i >= 0:
        ctx = s[max(0, i - 900):i + 500]
        ctx = re.sub(r'\s+', ' ', ctx)
        print(ctx[:1400])

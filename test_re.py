import re
s = '[video(video-tjdvcetC-1792831842736)(type-csdn)(url-https://live.csdn.net/v/embed/549853)(image-xxx)(title-yyy)]'
pat = r'\[video\([^\]]*?url-(https://live\.csdn\.net/v/embed/\d+)[^\]]*?\)\]'
r = re.sub(pat, r'<iframe src="\1"></iframe>', s)
print(r)

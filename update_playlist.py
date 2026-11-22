from urllib.request import Request, urlopen
from pathlib import Path

base = 'https://iptv-org.github.io/iptv/countries/'
entries = []
seen = set()
for country, label in [('sk', 'Slovensko'), ('cz', 'Cesko')]:
    request = Request(base + country + '.m3u', headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(request, timeout=45) as response:
        lines = response.read().decode('utf-8-sig').splitlines()
    count = 0
    for index, line in enumerate(lines):
        if line.startswith('#EXTINF:'):
            metadata = line
            extras = []
            j = index + 1
            while j < len(lines) and lines[j].startswith('#'):
                extras.append(lines[j]); j += 1
            if j >= len(lines):
                continue
            url = lines[j].strip()
            if not url.startswith(('http://', 'https://')) or url in seen:
                continue
            seen.add(url)
            if 'group-title=' in metadata:
                import re
                metadata = re.sub(r'group-title="[^"]*"', f'group-title="{label}"', metadata)
            else:
                metadata = metadata.replace('#EXTINF:', f'#EXTINF:-1 group-title="{label}" ', 1) if metadata.startswith('#EXTINF:-1,') else metadata
            entries.extend([metadata, *extras, url]); count += 1
    print(f'{label}: {count} streams')
if not entries:
    raise RuntimeError('No streams found; refusing to overwrite playlist')
Path('SK-CZ.m3u').write_text('#EXTM3U\n' + '\n'.join(entries) + '\n', encoding='utf-8')

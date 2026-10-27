import os
import re
import json
import anilist
import subprocess
import urllib.request
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

client = anilist.Client()

def pick(obj, key):
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)

def clean(text):
    text = text or ''
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.I)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    return text.strip()

def get_title(manga):
    t = manga.title
    return pick(t, 'english') or pick(t, 'romaji') or pick(t, 'native')

def get_date(manga):
    d = manga.start_date
    return pick(d, 'year'), pick(d, 'month'), pick(d, 'day')

def download_cover(manga, folder):
    cover = manga.cover
    url = pick(cover, 'extra_large') or pick(cover, 'large') or pick(cover, 'medium')
    if not url:
        print('No cover found')
        return None
    ext = os.path.splitext(url)[1] or '.jpg'
    path = os.path.join(folder, 'cover' + ext)
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(request) as r, open(path, 'wb') as f:
        f.write(r.read())
    print('Saved', path)
    return path

def get_format(manga_id):
    query = '''
    query ($id: Int) {
      Media(id: $id, type: MANGA) { format }
    }
    '''
    body = json.dumps({'query': query, 'variables': {'id': manga_id}}).encode()
    request = urllib.request.Request(
        'https://graphql.anilist.co',
        data=body,
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0',
        },
    )
    with urllib.request.urlopen(request) as r:
        data = json.loads(r.read().decode())
    return data['data']['Media']['format']

def make_comicinfo(manga, folder):
    year, month, day = get_date(manga)
    root = ET.Element('ComicInfo')

    ET.SubElement(root, 'Series').text = get_title(manga)
    ET.SubElement(root, 'Summary').text = clean(manga.description)
    ET.SubElement(root, 'Genre').text = ', '.join(manga.genres or [])
    ET.SubElement(root, 'Tags').text = ', '.join(manga.tags or [])
    ET.SubElement(root, 'Web').text = manga.url
    ET.SubElement(root, 'Notes').text = f'AniList ID: {manga.id}'
    ET.SubElement(root, 'Manga').text = 'YesAndRightToLeft'

    if year:
        ET.SubElement(root, 'Year').text = str(year)
    if month:
        ET.SubElement(root, 'Month').text = str(month)
    if day:
        ET.SubElement(root, 'Day').text = str(day)

    ET.indent(root)
    path = os.path.join(folder, 'ComicInfo.xml')
    ET.ElementTree(root).write(path, encoding='utf-8', xml_declaration=True)
    print('Saved', path)

def get_subjects(manga):
    return list(manga.genres or []) + list(manga.tags or [])

def get_date_text(manga):
    year, month, day = get_date(manga)
    if not year:
        return ''
    return f'{year}-{month or 1:02d}-{day or 1:02d}'

def make_opf(manga, folder):
    subject_xml = ''
    for s in get_subjects(manga):
        subject_xml += f'    <dc:subject>{escape(s)}</dc:subject>\n'

    date_xml = ''
    date = get_date_text(manga)
    if date:
        date_xml = f'    <dc:date>{date}</dc:date>\n'

    text = f'''<?xml version='1.0' encoding='utf-8'?>
<package xmlns='http://www.idpf.org/2007/opf' version='2.0'>
  <metadata xmlns:dc='http://purl.org/dc/elements/1.1/' xmlns:opf='http://www.idpf.org/2007/opf'>
    <dc:title>{escape(get_title(manga))}</dc:title>
    <dc:description>{escape(clean(manga.description))}</dc:description>
{subject_xml}{date_xml}    <dc:identifier opf:scheme='ANILIST'>{manga.id}</dc:identifier>
  </metadata>
</package>
'''
    path = os.path.join(folder, 'metadata.opf')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Saved', path)

def write_into_epub(manga, epub, cover_path):
    command = [
        'ebook-meta', epub,
        '--title', get_title(manga),
        '--comments', clean(manga.description),
        '--tags', ','.join(get_subjects(manga)),
        '--identifier', f'anilist:{manga.id}',
    ]
    date = get_date_text(manga)
    if date:
        command += ['--date', date]
    if cover_path:
        command += ['--cover', cover_path]
    try:
        subprocess.run(command, check=True)
        print('EPUB updated')
    except FileNotFoundError:
        print('ebook-meta not found. Install it with: sudo apt install calibre')
    except subprocess.CalledProcessError:
        print('ebook-meta failed')

def main():
    name = input('Enter a Series Name > ')
    results, page = client.search_manga(name, limit=5)
    if not results:
        print('Nothing found')
        return

    for i, m in enumerate(results, 1):
        print(i, get_title(m), m.id)
    choice = int(input('Number (Enter = 1) > ') or 1)
    manga = client.get_manga(results[choice - 1].id)

    try:
        fmt = get_format(manga.id)
    except Exception:
        fmt = None
    print('Format:', fmt)

    is_novel = fmt == 'NOVEL'

    folder = input('Save folder (Enter = here) > ') or '.'
    os.makedirs(folder, exist_ok=True)

    cover_path = download_cover(manga, folder)

    if is_novel:
        make_opf(manga, folder)
        epub = input('EPUB file to update (Enter = skip) > ').strip().strip('\'"')
        if epub:
            write_into_epub(manga, epub, cover_path)
    else:
        make_comicinfo(manga, folder)

if __name__ == '__main__':
    main()
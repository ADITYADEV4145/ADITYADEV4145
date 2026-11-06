"""Rotate the marked README GIF without changing other content."""
from html import escape
from pathlib import Path
import re
from urllib.request import Request, urlopen

GIFS = [
    ('https://media1.giphy.com/media/13HgwGsXF0aiGY/giphy.gif',
     'Animated developer working at a computer while the room catches fire'),
    ('https://media.giphy.com/media/LmNwrBhejkK9EFP504/giphy.gif',
     'Animated coding and typing scene'),
    ('https://media.giphy.com/media/ZVik7pBtu9dNS/giphy.gif',
     'Animated programmer working at a computer'),
    ('https://media.giphy.com/media/M9gbBd9nbDrOTu1Mqx/giphy.gif',
     'Animated developer illustration'),
]
START = '<!-- START:profile-gif -->'
END = '<!-- END:profile-gif -->'
BLOCK = re.compile(re.escape(START) + r'.*?' + re.escape(END), re.DOTALL)


def rotate(content):
    if content.count(START) != 1 or content.count(END) != 1:
        raise ValueError('Expected exactly one profile GIF section.')
    match = BLOCK.search(content)
    if not match:
        raise ValueError('Profile GIF markers are out of order.')
    current = re.search(r'src="([^"]+)"', match.group())
    urls = [url for url, _ in GIFS]
    if not current or current.group(1) not in urls:
        raise ValueError('Current GIF is not in the configured rotation.')
    url, alt = GIFS[(urls.index(current.group(1)) + 1) % len(GIFS)]
    block = (f'{START}\n<img align="right" src="{escape(url, quote=True)}" '
             f'width="300" alt="{escape(alt, quote=True)}" />\n{END}')
    return content[:match.start()] + block + content[match.end():], url


def check_gif(url):
    request = Request(url, headers={'User-Agent': 'AdityaProfile-GIF-Rotation/1.0'})
    with urlopen(request, timeout=20) as response:
        if response.headers.get_content_type() != 'image/gif':
            raise ValueError('The next image is not served as a GIF.')
        if response.read(6) not in (b'GIF87a', b'GIF89a'):
            raise ValueError('The next image has an invalid GIF header.')


if __name__ == '__main__':
    readme = Path(__file__).resolve().parents[1] / 'README.md'
    updated, url = rotate(readme.read_text(encoding='utf-8'))
    # Leave README unchanged if the selected image is unavailable.
    check_gif(url)
    readme.write_text(updated, encoding='utf-8')
    print(f'Rotated profile GIF to {url}')

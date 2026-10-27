# anilist-metadata

A small Python tool that makes metadata files for your comics and light novels, using [AniList](https://anilist.co).

- **Comics (CBZ):** makes `ComicInfo.xml`
- **Light novels (EPUB):** makes `metadata.opf` (and can write the data into the EPUB)
- Downloads the best cover and saves it as `cover.jpg` or `cover.png`
- Finds out by itself if the title is a manga or a light novel

## Requirements

- Python 3.9 or newer
- [python-anilist](https://pypi.org/project/python-anilist/)
- Calibre (optional, only to write metadata into an EPUB file)

```
pip install -r requirements.txt
sudo apt install calibre
```

or

```
pip install python-anilist
sudo apt install calibre
```

## Usage

```
python3 anilist-metadata.py
```

1. Type the name of the manga or novel.
2. Pick the right result by number.
3. Type a save folder (or press Enter for the current folder).
4. For light novels, you can type the path of an EPUB file to update it.

## Output

| Type | Files |
| --- | --- |
| Comic | `ComicInfo.xml`, `cover.*` |
| Light novel | `metadata.opf`, `cover.*` |

## Example

<pre>
Enter a Series Name > Dragon Ball
1 Dragon Ball 30042
2 Dragon Ball Super 86508
3 Dragon Ball: That Time I Got Reincarnated as Yamcha! 98030
4 Cross Epoch 30881
5 Dragon Ball: Episode of Bardock 56373
Number (Enter = 1) > 1
Format: MANGA
Save folder (Enter = here) > example
Saved example/cover.jpg
Saved <a href="example/ComicInfo.xml">example/ComicInfo.xml</a>
</pre>

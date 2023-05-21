# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
#

import contextlib
import functools
import logging
import re
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import ContextManager, Iterable, Iterator, List, Optional, Sequence
from urllib.parse import urlparse

import func_argparse
from bs4 import BeautifulSoup  # type: ignore

from cc_net import jsonql

WET_URL_ROOT = "https://data.commoncrawl.org"


logger = logging.getLogger(__name__)


def cc_wet_paths_url(dump_id: str) -> str:
    return "/".join([WET_URL_ROOT, "crawl-data", "CC-MAIN-" + dump_id, "wet.paths.gz"])


@functools.lru_cache()
def cc_segments(dump_id: str, cache_dir: Path = None) -> List[str]:
    wet_paths = cc_wet_paths_url(dump_id)
    cache_dir = cache_dir or jsonql._tmp_dir()
    wet_paths_cache = cache_dir / f"wet_{dump_id}.paths.gz"
    f = jsonql.open_remote_file(wet_paths, cache=wet_paths_cache)
    return [segment.strip() for segment in f]


def list_dumps() -> List[str]:
    home_page = BeautifulSoup(
        urllib.request.urlopen("http://index.commoncrawl.org/"), features="html.parser"
    )
    dumps = [a.get("href").strip("/") for a in home_page.findAll("a")]
    dumps = [a[8:] for a in dumps if re.match(r"^CC-MAIN-\d\d\d\d-\d\d$", a)]

    return sorted(dumps)


def ls():
    for dump in list_dumps():
        print(dump, "->", cc_wet_paths_url(dump))


def parse_doc(headers: List[str], doc: List[str]) -> Optional[dict]:
    """Headers format is:
    WARC/1.0
    WARC-Type: conversion
    WARC-Target-URI: [url]
    WARC-Date: [crawldate: 2019-02-15T19:15:59Z]
    WARC-Record-ID: <urn:uuid:8865156e-d5f1-4734-9c68-4b46eaf2bb7e>
    WARC-Refers-To: <urn:uuid:340152e2-65cf-4143-b522-8ce4e2d069d7>
    WARC-Block-Digest: sha1:S3DTWCONT2L6ORTGCY2KXEZ37LNBB7V2
    Content-Type: text/plain
    Content-Length: 7743

    ['WARC/1.0', 
    'WARC-Type: conversion',
    'WARC-Target-URI: https://zw.lt/kultura-historia/wilno-zamienilo-sie-w-galerie-sztuki-pod-otwartym-niebem/', 
    'WARC-Date: 2023-03-20T09:53:29Z', 
    'WARC-Record-ID: <urn:uuid:0cc0ce8c-ba9b-49a2-a6e0-d93b2ea65766>', 
    'WARC-Refers-To: <urn:uuid:fc2f4e32-d5b8-45e7-b65f-f083c27237c9>', 
    'WARC-Block-Digest: sha1:IJDXNKVVS2DY7V5YHW7BJUBKY7TGMFBH', 
    'WARC-Identified-Content-Language: pol', 
    'Content-Type: text/plain', 
    'Content-Length: 2774', ''], 
    ['Wilno zamieniło się w galerię sztuki pod otwartym niebem - Wiadomości Znad Wilii Wilno zamieniło się w galerię sztuki pod otwartym niebem - Wiadomości Znad Wilii', 'Wilno i Wileńszczyzna', 'Galeria', 'Opinie', 'Radar Wileński', 'KATEGORIE', 'Świat', 'Litwa', 'Gospodarka', 'Kultura i Historia', 'Religia', 'Rozmaitości', 'Sport', 'Solidarni z Białorusią', 'Radio', 'Salon polityczny', 'Szósty dzień tygodnia', 'Rewitalizacja przestrzeni publicznej', 'Ziarno wiary', 'Koncert Życzeń', 'Lista PL', 'Kultura i Historia', '7 lipca, 2020 18:54', 'Wilno zamieniło się w galerię sztuki pod otwartym niebem', '„Sztuka bez dachu” – 100 artystów przez 3 tygodnie będzie eksponować w centrum Wilna swoje dzieła na tablicach reklamowych m. in. typu Citylight.', 'vilnius.lt', 'Fot. BNS/Julius Kalinskas', 'Prace możemy też podziwiać w galerii internetowej www.menasbestogo.lt. Celem projektu jest zachęcenie mieszkańców Wilna do interesowania się sztuką, ale także do nabywania dzieł i tym samym wspierania artystów.', 'Projekt zrodził się w czasie pandemii, gdy nie działały galerie sztuki oraz artyści nie mogli eksponować i sprzedawać swoich dzieł.', 'Prace będzie można oglądać na wileńskich ulicach do 28 lipca, ale wirtualna galeria będzie czynna dłużej.', 'Organizatorzy projektu – Samorząd miasta Wilna i spółka reklamy ulicznej JCDecaux Lietuva.', 'TAGI:', 'Menas be stogo', 'Sztuka', 'REKLAMA', 'PODCASTY I GALERIE', 'Szósty dzień tygodnia', 'Podcast', '6 dzień tygodnia – 18.03.2023', 'Rozmaitości', 'Podcast', 'Niezwykłe pasje – Niezwykłych ludzi. Dr Jerzy Marek Nowakowski', 'Kultura i Historia', 'Podcast', 'Ludzie Kulturalni – Stanisław Górka', 'Salon polityczny', 'Podcast', 'Premiera filmu „Żywioł” już dzisiaj: rozmowa z producentką T.Różanowską', 'Rewitalizacja przestrzeni publicznej', 'Podcast', 'Agencja VIPA – źródłem finansowania programu termomodernizacji', 'Salon polityczny', 'Podcast', 'J. Narkiewicz o kandytowaniu na mera rejonu trockiego', 'Galeria', 'Wilno i Wileńszczyzna', 'Premiera filmu „Żywioł” w Pałacu Władców', 'Galeria', 'Wilno i Wileńszczyzna', 'Wystawa „Bezpieczeństwo i ochrona infrastruktury krytycznej”', 'Galeria', 'Wilno i Wileńszczyzna', 'Kaziuczek Niemenczyński 2023', 'Portal', 'Wilno i Wileńszczyzna', 'Galeria', 'Opinie', 'Radar Wileński', 'Świat', 'Litwa', 'Gospodarka', 'Kultura i Historia', 'Religia', 'Sport', 'Rozmaitości', 'Radio', 'Salon polityczny', 'Szósty dzień tygodnia', 'Rewitalizacja przestrzeni publicznej', 'Ziarno wiary', 'Koncert Życzeń', 'Lista PL', 'Projekt jest finansowany ze środków Kancelarii Prezesa Rady Ministrów RP w ramach konkursu „Polonia i Polacy za Granicą 2023”. Publikacja wyraża jedynie poglądy autorów i nie może być utożsamiana z oficjalnym stanowiskiem Kancelarii Prezesa Rady Ministrów RP ani Fundacji „Pomoc Polakom na Wschodzie”.', 'Radio Znad Wilii', 'Portal zw.lt', 'Reklama', 'Pracownicy', 'Brandbook', 'Rekwizyty', '', ''])
    """
    if not headers or not doc:
        return None

    try:
        warc_type = headers[1].split()[1]
        if warc_type != "conversion":
            return None
        
        headerDic = {}
        for header in headers:
            if len(header.split()) >= 2:
                headerDic[header.split()[0]] = header.split()[1]
        url = ("WARC-Target-URI:" in headerDic) and headerDic["WARC-Target-URI:"] or ""
        date = ("WARC-Date:" in headerDic) and headerDic["WARC-Date:"] or ""
        digest = ("WARC-Block-Digest:" in headerDic) and headerDic["WARC-Block-Digest:"] or ""
        length = ("Content-Length:" in headerDic) and headerDic["Content-Length:"] or 0
        language = ("WARC-Identified-Content-Language:" in headerDic) and headerDic["WARC-Identified-Content-Language:"] or ""
    except Exception as e:
        logger.warning("Can't parse header:", e, headers, doc)
        return None

    # Docs are separated by two empty lines.
    last = None
    if not doc[-1] and not doc[-2]:
        last = -2
    title, doc = doc[0], doc[1:last]

    return {
        "url": url,
        "date_download": date,
        "digest": digest,
        "length": length,
        "nlines": len(doc),
        "language":language,
        "source_domain": urlparse(url).netloc,
        "title": title,
        "raw_content": "\n".join(doc),
    }


def group_by_docs(warc_lines: Iterable[str]) -> Iterable[dict]:
    doc: List[str] = []
    headers, read_headers = [], True
    for warc in warc_lines:
        warc = warc.strip()
        if read_headers:
            headers.append(warc)
            read_headers = warc != ""
            continue

        if warc == "WARC/1.0":
            # We reached the beginning of the new doc.
            parsed = parse_doc(headers, doc)
            if parsed is not None:
                yield parsed
            headers, doc, read_headers = [warc], [], True
            continue

        doc.append(warc)

    # Return the last document
    if doc:
        parsed = parse_doc(headers, doc)
        if parsed is not None:
            yield parsed


def parse_warc_file(lines: Iterable[str], min_len: int = 1) -> Iterator[dict]:
    n_doc = 0
    n_ok = 0
    for doc in group_by_docs(lines):
        n_doc += 1
        if not doc or len(doc["raw_content"]) < min_len:
            continue
        n_ok += 1
        yield doc
    if n_doc > 0:
        logger.info(f"Kept {n_ok:_d} documents over {n_doc:_d} ({n_ok / n_doc:.1%}).")
    else:
        logger.info(f"Found no documents")


def dl(
    dump: str,
    shard: int,
    num_shards: int,
    output: Path = None,
    num_segments_per_shard: int = 0,
):
    """Download a shard of the common crawl, and export it to json.

    Arguments:
        output: filename of the output file
        dump: CC dump id
        shard: id of the shard
        num_shards: total number of shards
        num_segments_per_shard: manual control of the number of segment per shard.
    """
    reader = CCShardReader(dump, shard, num_shards, num_segments_per_shard)
    jsonql.run_pipes(inputs=reader, output=output)
    logger.info(f"Done. {output} is ready.")


class CCSegmentsReader(Iterable[dict]):
    def __init__(
        self, segments: Sequence[str], min_len: int = 0, cache_dir: Path = None
    ):
        self._segments = segments
        self.min_len = min_len
        if cache_dir is not None:
            cache_dir = Path(cache_dir)
            cache_dir.mkdir(exist_ok=True)
        self.cache_dir = cache_dir
        self.retrieved_segments = 0

    def segment_url(self, segment: str):
        return "/".join((WET_URL_ROOT, segment))

    @property
    def segments(self) -> Sequence[str]:
        return self._segments

    def open_segment(self, segment: str) -> Iterable[str]:
        url = self.segment_url(segment)
        file: Optional[Path] = None
        if self.cache_dir:
            file = self.cache_dir / segment.split("/")[-1]
        if not file or not file.exists():
            self.retrieved_segments += 1

        return jsonql.open_remote_file(url, cache=file)

    def __iter__(self) -> Iterator[dict]:
        n = len(self.segments)
        for i, segment in enumerate(self.segments):
            start = time.time()
            # TODO: start downloading the next segment in the background
            for doc in parse_warc_file(self.open_segment(segment), self.min_len):
                doc["cc_segment"] = segment
                yield doc

            if i + 1 >= n:
                continue
            end = time.time()
            delay = (end - start) / 3600 * (n - 1 - i)
            logger.info(
                f"Parsed {i + 1} / {n} files. Estimated remaining time: {delay:.1f}h"
            )


class CCShardReader(CCSegmentsReader):
    def __init__(
        self,
        dump: str,
        shard: int,
        num_shards: int = -1,
        num_segments_per_shard: int = 40,
        min_len: int = 300,
        cache_dir: Path = None,
    ):
        """Downloads a shard of Common Crawl, and yields dict.

        Arguments:
            dump: CC dump id
            shard: id of the shard
            num_shards: total number of shards
            num_segments_per_shard: if set will limit the number of files by shard.
                Useful for testing.
        """
        super().__init__([], min_len=min_len, cache_dir=cache_dir)
        self.dump = dump
        self.shard = shard
        assert num_shards > 0 or num_segments_per_shard > 0
        self.num_shards = num_shards
        self.num_segments_per_shard = num_segments_per_shard

    @property
    def segments(self) -> Sequence[str]:
        # Delaying the initialization allows to delay the looking up of the WET files
        if self._segments:
            return self._segments
        #2023-14 n = 80000
        segments = cc_segments(self.dump, self.cache_dir)
        n = len(segments)
        if self.num_shards < 0:
            self.num_shards = n // self.num_segments_per_shard
        i_min = (self.shard * n) // self.num_shards
        i_max = ((self.shard + 1) * n) // self.num_shards
        if self.num_segments_per_shard > 0:
            i_max = min(i_max, i_min + self.num_segments_per_shard)
        self._segments = segments[i_min:i_max]
        return self._segments


def _tmp(prefix: str = None, suffix: str = None, dir: Path = None) -> Path:
    _, tmp_path = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=dir)
    return Path(tmp_path)


@contextlib.contextmanager
def timer(name: str = "-"):
    start = time.time()
    yield None
    delay = time.time() - start
    print(f"{name} took {delay:.1f}s")


def benchmark(tmp_path: Path):
    segments = [
        "crawl-data/CC-MAIN-2019-09/segments/1550249406966.99/wet/CC-MAIN-20190222220601-20190223002601-00441.warc.wet.gz"
    ]
    seg_file = tmp_path / "CC-MAIN-20190222220601-20190223002601-00441.warc.wet.gz"

    with timer("from network"):
        list(CCSegmentsReader(segments))

    with timer("from network, with caching"):
        list(CCSegmentsReader(segments, cache_dir=tmp_path))
    assert seg_file.exists()

    with timer("from disk"):
        CCSegmentsReader(segments, cache_dir=tmp_path)
    seg_file.unlink()


if __name__ == "__main__":
    func_argparse.main(ls, dl)

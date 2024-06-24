#! /usr/bin/python3

__copyright__ = "(C) 2018-2024 Guido Draheim"
__contact__ = "https://github.com/gdraheim/docker-mirror-packages-repo"
__license__ = "CC0 Creative Commons Zero (Public Domain)"
__version__ = "1.7.6261"

import xml.dom.minidom as minidom
import os.path as path
import os
import gzip
import hashlib

import logging
logg = logging.getLogger("FIX")


def fix(datafile: str) -> None:
    logg.info("reading %s", datafile)
    repodatadir = path.dirname(datafile)
    repodata = path.basename(repodatadir)
    fixes = 0
    dom = minidom.parse(datafile)
    for data in dom.getElementsByTagName("data"):
        kind = data.getAttribute("type")
        locs = data.getElementsByTagName("location")
        loc = locs[0]
        href = loc.getAttribute("href")
        repohref = path.join(repodatadir, path.basename(href))
        if path.exists(href) or path.exists(repohref):
            logg.info("%s exists %s", kind, href)
        else:
            logg.info("%s missing %s", kind, href)
            basename = path.basename(href)
            dirsname = path.dirname(href)
            if "-" in basename:
                found = ""
                suffix = basename.split("-")[-1]
                for dirpath, dirnames, filenames in os.walk(repodatadir):
                    for filename in filenames:
                        if filename.endswith("-" + suffix):
                            found = path.join(dirpath, filename)
            if found:
                newhref = path.join(repodata, path.basename(found))
                logg.info("%s having: %s", kind, newhref)
                xmlgz = open(found, "rb").read()
                checksum_gz = hashlib.sha256(xmlgz).hexdigest()
                logg.info("%s        checksum: %s", kind, checksum_gz)
                xml = gzip.open(found, "rb").read()
                checksum_xml = hashlib.sha256(xml).hexdigest()
                logg.info("%s   open checksum: %s", kind, checksum_xml)
                a = data.getElementsByTagName("location")
                a[0].setAttribute("href", newhref)
                b = data.getElementsByTagName("checksum")
                b[0].firstChild.replaceWholeText(checksum_gz)  # type: ignore[union-attr]
                c = data.getElementsByTagName("size")
                c[0].firstChild.replaceWholeText(str(len(xmlgz)))  # type: ignore[union-attr]
                d = data.getElementsByTagName("open-size")
                d[0].firstChild.replaceWholeText(str(len(xml)))  # type: ignore[union-attr]
                e = data.getElementsByTagName("open-checksum")
                e[0].firstChild.replaceWholeText(checksum_xml)  # type: ignore[union-attr]
                fixes += 1
    if fixes:
        logg.debug("done %i fixes -> overwrite repomd.xml", fixes)
        os.rename(datafile, datafile + ".old")
        dom.writexml(open(datafile, "w"))
        logg.warning("done %i fixes -> %s", fixes, datafile)


if __name__ == "__main__":
    from argparse import ArgumentParser
    _o = ArgumentParser()
    _o.add_argument("-v", "--verbose", action="count", default=0,
                    help="increase logging level")
    _o.add_argument("repomd", default="repodata/repomd.xml",
                    help="the repomd to be fixed")
    opt = _o.parse_args()
    logging.basicConfig(level=max(0, logging.ERROR - 10 * opt.verbose))
    fix(opt.repomd)

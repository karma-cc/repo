#!/usr/bin/env python3
"""Regenerate Packages / Packages.bz2 / Release from debs/*.deb (pure stdlib)."""
import bz2, hashlib, io, os, tarfile, time, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
DEBS = os.path.join(ROOT, "debs")
SUITE = "stable"
ARCHS = "iphoneos-arm iphoneos-arm64 iphoneos-arm64e"
ORIGIN = "karma-cc Repo"

def parse_control(text):
    fields, key = {}, None
    for line in text.splitlines():
        if line.startswith(" ") and key and key in fields:
            fields[key].append(line[1:])
        elif ":" in line:
            k, v = line.split(":", 1)
            key = k.strip()
            fields[key] = [v.strip()]
        else:
            key = None
    return {k: "\n".join(v) for k, v in fields.items()}

def read_deb_control(path):
    with open(path, "rb") as f:
        assert f.read(8) == b"!<arch>\n", f"not an ar archive: {path}"
        while True:
            hdr = f.read(60)
            if len(hdr) < 60:
                break
            name = hdr[:16].decode().rstrip(" /")
            size = int(hdr[48:58].decode().strip())
            payload = f.read(size)
            if size % 2 == 1:
                f.read(1)
            if name.startswith("control.tar"):
                tio = io.BytesIO(payload)
                with tarfile.open(fileobj=tio, mode="r:*") as tf:
                    for m in tf.getmembers():
                        if m.name.rstrip("/") in ("./control", "control"):
                            return tf.extractfile(m).read().decode()
    raise RuntimeError(f"no control found in {path}")

def sha(data, name):
    h = hashlib.new(name)
    h.update(data)
    return h.hexdigest()

def main():
    entries = []
    for deb in sorted(glob.glob(os.path.join(DEBS, "*.deb"))):
        with open(deb, "rb") as f:
            raw = f.read()
        c = parse_control(read_deb_control(deb))
        rel = os.path.relpath(deb, ROOT).replace("\\", "/")
        need = ["Package", "Version", "Architecture", "Maintainer", "Description"]
        missing = [n for n in need if n not in c]
        if missing:
            print(f"skip {rel}: missing fields {missing}")
            continue
        c["Filename"] = rel
        c["Size"] = str(len(raw))
        c["MD5sum"] = sha(raw, "md5")
        c["SHA1"] = sha(raw, "sha1")
        c["SHA256"] = sha(raw, "sha256")
        c["Section"] = c.get("Section", "Tweaks")
        c["Depends"] = c.get("Depends", "")
        order = ["Package", "Version", "Architecture", "Maintainer", "Depends",
                 "Section", "Filename", "Size", "MD5sum", "SHA1", "SHA256", "Description"]
        lines = []
        for k in order:
            if k in c:
                first, *rest = c[k].split("\n")
                lines.append(f"{k}: {first}")
                lines += [" " + l for l in rest]
        entries.append("\n".join(lines))
    pkgs = ("\n\n".join(entries) + ("\n" if entries else "")).encode()
    with open(os.path.join(ROOT, "Packages"), "wb") as f:
        f.write(pkgs)
    with open(os.path.join(ROOT, "Packages.bz2"), "wb") as f:
        f.write(bz2.compress(pkgs, 9))
    date = time.strftime("%a, %d %b %Y %H:%M:%S UTC", time.gmtime())
    rel = io.StringIO()
    rel.write(f"Origin: {ORIGIN}\n")
    rel.write(f"Label: {ORIGIN}\n")
    rel.write(f"Suite: {SUITE}\n")
    rel.write("Version: 1.0\n")
    rel.write(f"Codename: {SUITE}\n")
    rel.write(f"Architectures: {ARCHS}\n")
    rel.write("Components: main\n")
    rel.write(f"Date: {date}\n")
    rel.write("Description: karma-cc 越狱源\n")
    for algo in ("MD5Sum", "SHA1", "SHA256"):
        rel.write(f"{algo}:\n")
        hname = "md5" if algo == "MD5Sum" else algo.lower()
        for fname in ("Packages", "Packages.bz2"):
            with open(os.path.join(ROOT, fname), "rb") as f:
                data = f.read()
            rel.write(f" {sha(data, hname)} {len(data):16d} {fname}\n")
    with open(os.path.join(ROOT, "Release"), "w") as f:
        f.write(rel.getvalue())
    print(f"Packages: {len(entries)} entries -> Packages / Packages.bz2 / Release")

if __name__ == "__main__":
    main()

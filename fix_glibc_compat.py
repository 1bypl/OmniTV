#!/usr/bin/env python3
"""Obniza wymagania GLIBC w gotowym bundlu PyInstallera.

Na nowszych dystrybucjach (np. glibc 2.43/2.44) linker przypisuje czesc
funkcji libc/libm do nowych wersji symboli (np. ``cosh@GLIBC_2.44``),
mimo ze stare wersje (``GLIBC_2.2.5``) nadal istnieja i dzialaja tak samo.
Taki bundle nie uruchomi sie na starszych systemach (np. Ubuntu 24.04,
glibc 2.39), choc moglby.

Narzedzie podmienia nazwe wymaganej wersji tylko dla bezpiecznych,
niezmienionych funkcji libc/libm, przepisujac odnosnik do istniejacego
wpisu ``GLIBC_2.2.5``. Nie zmienia kodu ani ukladu sekcji.

Jesli plik wymaga nowszej glibc z powodu funkcji spoza listy bezpiecznych,
narzedzie konczy sie bledem, zeby nie utworzyc cicho niekompatybilnego
pakietu.

Nie wymaga zadnych zewnetrznych bibliotek - czyta format ELF bezposrednio.

Uzycie:
    python3 fix_glibc_compat.py build/linux-dist/OmniTV
    python3 fix_glibc_compat.py --check build/linux-dist/OmniTV
"""

from __future__ import annotations

import argparse
import os
import struct
import sys

# Funkcje, ktorych stare wersje (GLIBC_2.2.5) sa rownowazne nowym.
# Sa to standardowe funkcje libc/libm o stabilnej semantyce.
SAFE_SYMBOLS = {
    # libm - trygonometria i funkcje hiperboliczne
    "sin", "sinf", "cos", "cosf", "tan", "tanf",
    "asin", "asinf", "acos", "acosf", "atan", "atanf",
    "atan2", "atan2f", "sinh", "sinhf", "cosh", "coshf",
    "tanh", "tanhf", "asinh", "asinhf", "acosh", "acoshf",
    "atanh", "atanhf",
    # libm - wykladnicze i logarytmy
    "exp", "expf", "exp2", "exp2f", "expm1", "expm1f",
    "log", "logf", "log2", "log2f", "log10", "log10f",
    "log1p", "log1pf", "pow", "powf", "sqrt", "sqrtf",
    "cbrt", "cbrtf", "hypot", "hypotf",
    # libm - pozostale
    "fabs", "fabsf", "floor", "floorf", "ceil", "ceilf",
    "trunc", "truncf", "round", "roundf", "rint", "rintf",
    "nearbyint", "nearbyintf", "lrint", "lrintf",
    "llrint", "llrintf", "lround", "lroundf", "llround", "llroundf",
    "fmod", "fmodf", "remainder", "remainderf", "fma", "fmaf",
    "copysign", "copysignf", "nextafter", "nextafterf",
    "fdim", "fdimf", "fmax", "fmaxf", "fmin", "fminf",
    "scalbn", "scalbnf", "ilogb", "ilogbf", "logb", "logbf",
    "frexp", "frexpf", "ldexp", "ldexpf", "modf", "modff",
    "nan", "nanf", "erf", "erff", "erfc", "erfcf",
    "tgamma", "tgammaf", "lgamma", "lgammaf",
    # libc - terminal (termios)
    "cfgetospeed", "cfsetospeed", "cfgetispeed", "cfsetispeed",
}

BASE_VERSION = "GLIBC_2.2.5"

# e_machine dla platform, ktore nas interesuja.
SUPPORTED_MACHINES = {
    3,    # EM_386
    62,   # EM_X86_64
    183,  # EM_AARCH64
    40,   # EM_ARM
}


class ElfError(Exception):
    pass


def _parse_version(text: str) -> tuple[int, ...]:
    return tuple(int(part) for part in text.split("."))


def _read_cstring(blob: bytes, offset: int) -> str:
    end = blob.find(b"\x00", offset)
    if end < 0:
        end = len(blob)
    return blob[offset:end].decode("ascii", "replace")


class ElfFile:
    """Minimalny czytnik ELF (little-endian, 32/64-bit)."""

    def __init__(self, path: str):
        self.path = path
        with open(path, "rb") as handle:
            self.data = handle.read()

        if self.data[:4] != b"\x7fELF":
            raise ElfError("to nie jest plik ELF")
        ei_class = self.data[4]
        ei_data = self.data[5]
        if ei_data != 1:
            raise ElfError("tylko little-endian")
        if ei_class == 2:
            self.is64 = True
        elif ei_class == 1:
            self.is64 = False
        else:
            raise ElfError("nieznana klasa ELF")

        if self.is64:
            header = struct.unpack_from("<16sHHIQQQIHHHHHH", self.data, 0)
            (self.e_shoff, self.e_shentsize, self.e_shnum,
             self.e_shstrndx) = header[6], header[11], header[12], header[13]
            self.e_machine = header[2]
        else:
            header = struct.unpack_from("<16sHHIIIIIHHHHHH", self.data, 0)
            (self.e_shoff, self.e_shentsize, self.e_shnum,
             self.e_shstrndx) = header[6], header[11], header[12], header[13]
            self.e_machine = header[2]

        if self.e_shoff == 0 or self.e_shnum == 0:
            raise ElfError("brak tablicy sekcji")

        self.sections = self._read_sections()
        shstr = self.sections[self.e_shstrndx]
        names_blob = self.data[shstr["offset"]:shstr["offset"] + shstr["size"]]
        for section in self.sections:
            section["name"] = _read_cstring(names_blob, section["name_offset"])

    def _read_sections(self):
        sections = []
        for index in range(self.e_shnum):
            offset = self.e_shoff + index * self.e_shentsize
            if self.is64:
                fields = struct.unpack_from("<IIQQQQIIQQ", self.data, offset)
                name_off, sh_type, _flags, _addr, sh_offset, sh_size = fields[:6]
                link, _info, _align, entsize = fields[6:10]
            else:
                fields = struct.unpack_from("<IIIIIIIIII", self.data, offset)
                name_off, sh_type, _flags, _addr, sh_offset, sh_size = fields[:6]
                link, _info, _align, entsize = fields[6:10]
            sections.append({
                "name_offset": name_off,
                "type": sh_type,
                "offset": sh_offset,
                "size": sh_size,
                "link": link,
                "entsize": entsize,
            })
        return sections

    def section(self, name: str):
        for section in self.sections:
            if section.get("name") == name:
                return section
        return None

    def section_data(self, name: str) -> bytes:
        section = self.section(name)
        if section is None:
            return b""
        return self.data[section["offset"]:section["offset"] + section["size"]]

    def symbols_by_version_index(self) -> dict[int, list[str]]:
        """Mapuje indeks wersji (z .gnu.version) na nazwy symboli."""
        version_section = self.section(".gnu.version")
        dynsym = self.section(".dynsym")
        if version_section is None or dynsym is None:
            return {}
        dynstr = self.section_data(".dynstr")
        versym_blob = self.section_data(".gnu.version")
        entsize = dynsym["entsize"] or (24 if self.is64 else 16)
        count = dynsym["size"] // entsize
        sym_off = dynsym["offset"]
        result: dict[int, list[str]] = {}
        for index in range(count):
            if index * 2 + 2 > len(versym_blob):
                break
            ndx = struct.unpack_from("<H", versym_blob, index * 2)[0] & 0x7FFF
            st_name = struct.unpack_from("<I", self.data, sym_off + index * entsize)[0]
            result.setdefault(ndx, []).append(_read_cstring(dynstr, st_name))
        return result

    def version_entries(self):
        """Zwraca wpisy Vernaux z .gnu.version_r wraz z offsetem w pliku."""
        section = self.section(".gnu.version_r")
        if section is None:
            return []
        data = self.section_data(".gnu.version_r")
        section_offset = section["offset"]
        entries = []
        verneed_offset = 0
        while verneed_offset + 16 <= len(data):
            _vn_version, vn_cnt, _vn_file, vn_aux, vn_next = struct.unpack_from(
                "<HHIII", data, verneed_offset
            )
            aux_offset = verneed_offset + vn_aux
            for _ in range(vn_cnt):
                if aux_offset + 16 > len(data):
                    break
                vna_hash, vna_flags, vna_other, vna_name, vna_next = struct.unpack_from(
                    "<IHHII", data, aux_offset
                )
                entries.append({
                    "abs": section_offset + aux_offset,
                    "hash": vna_hash,
                    "flags": vna_flags,
                    "other": vna_other,
                    "name_offset": vna_name,
                    "next": vna_next,
                })
                if vna_next == 0:
                    break
                aux_offset += vna_next
            if vn_next == 0:
                break
            verneed_offset += vn_next

        dynstr = self.section_data(".dynstr")
        for entry in entries:
            entry["name"] = _read_cstring(dynstr, entry["name_offset"])
        return entries


def _iter_elf_files(root: str):
    for dirpath, _dirnames, filenames in os.walk(root):
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            if os.path.islink(path) or not os.path.isfile(path):
                continue
            try:
                with open(path, "rb") as handle:
                    if handle.read(4) != b"\x7fELF":
                        continue
            except OSError:
                continue
            yield path


def analyze(path: str, max_version: tuple[int, ...]):
    """Zwraca (wpisy_do_poprawy, nieobslugiwane_wymagania)."""
    elf = ElfFile(path)
    if elf.e_machine not in SUPPORTED_MACHINES:
        return [], []
    entries = elf.version_entries()
    if not entries:
        return [], []
    base = next((e for e in entries if e["name"] == BASE_VERSION), None)
    symbols = elf.symbols_by_version_index()

    patchable = []
    remaining = []
    for entry in entries:
        name = entry["name"]
        if not name.startswith("GLIBC_"):
            continue
        version = _parse_version(name[len("GLIBC_"):])
        if version <= max_version:
            continue
        used = set(symbols.get(entry["other"], []))
        if base is not None and (not used or used <= SAFE_SYMBOLS):
            entry["base_hash"] = base["hash"]
            entry["base_name_offset"] = base["name_offset"]
            patchable.append((entry, sorted(used)))
        else:
            remaining.append((name, sorted(used)))
    return patchable, remaining


def apply_patches(path: str, patches) -> list[str]:
    changes = []
    if not patches:
        return changes
    with open(path, "r+b") as handle:
        for entry, used in patches:
            # vna_hash (offset 0) i vna_name (offset 8) w 16-bajtowym wpisie.
            handle.seek(entry["abs"])
            handle.write(struct.pack("<I", entry["base_hash"]))
            handle.seek(entry["abs"] + 8)
            handle.write(struct.pack("<I", entry["base_name_offset"]))
            changes.append(f"{entry['name']} -> {BASE_VERSION} ({', '.join(used)})")
    return changes


def process_file(path: str, max_version: tuple[int, ...], check_only: bool):
    patchable, remaining = analyze(path, max_version)
    if not patchable and not remaining:
        return True, []
    if remaining:
        details = "; ".join(f"{name}: {', '.join(syms)}" for name, syms in remaining)
        return False, [f"{path}: nieobslugiwane wymagania ({details})"]
    if check_only:
        return True, [f"{path}: wymaga poprawy ({len(patchable)} wpisow)"]
    changes = apply_patches(path, patchable)
    return True, [f"{path}: {change}" for change in changes]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Obniza wymagania GLIBC w bundlu PyInstallera."
    )
    parser.add_argument("path", help="katalog bundla lub pojedynczy plik ELF")
    parser.add_argument(
        "--max-glibc",
        default="2.39",
        help="maksymalna dozwolona wersja glibc (domyslnie 2.39)",
    )
    parser.add_argument(
        "--check", action="store_true", help="tylko sprawdz, nie modyfikuj"
    )
    parser.add_argument("--quiet", action="store_true", help="mniej komunikatow")
    args = parser.parse_args(argv)

    max_version = _parse_version(args.max_glibc)
    targets = list(_iter_elf_files(args.path)) if os.path.isdir(args.path) else [args.path]

    failures = []
    changed = 0
    for target in targets:
        try:
            ok, messages = process_file(target, max_version, args.check)
        except (ElfError, OSError, struct.error) as exc:
            failures.append(f"{target}: {exc}")
            continue
        if not ok:
            failures.extend(messages)
            continue
        for message in messages:
            changed += 1
            if not args.quiet:
                print(message)

    if failures:
        print(
            f"\nBLAD: bundle wymaga nowszej glibc niz {args.max_glibc}:",
            file=sys.stderr,
        )
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    if changed == 0:
        if not args.quiet:
            print(f"OK: wszystkie pliki ELF sa zgodne z glibc <= {args.max_glibc}.")
    elif args.check:
        print(f"\n{changed} plik(ow) wymaga poprawki (tryb --check).")
    else:
        print(f"\nPoprawiono {changed} plik(ow) ELF.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

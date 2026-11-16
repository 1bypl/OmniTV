# OmniTV

**Autor:** [1bypl](https://github.com/1bypl)

OmniTV to lekki desktopowy odtwarzacz publicznych kanałów TV i strumieni dla
Linuksa i Windows. Korzysta z bazy [iptv-org](https://github.com/iptv-org/api),
wbudowanego odtwarzacza **libmpv** oraz `yt-dlp` do otwierania obsługiwanych
serwisów streamingowych. Interfejs jest dostępny w 7 językach, tłumaczy napisy
kanału i nagrywa strumień bez rekompresji.

Aktualna wersja: **0.2.0**.

## Najważniejsze funkcje

- Przeglądanie i odtwarzanie tysięcy darmowych kanałów IPTV z filtrami:
  wyszukiwanie, kraj, kategoria, ulubione.
- Interfejs w 7 językach: **polski, angielski, niemiecki, rosyjski, francuski,
  włoski i hiszpański**. Język zmienia się bez restartu i jest zapamiętywany.
- Tłumaczone nazwy krajów, kategorii, motywów, przycisków i komunikatów.
- Wyszukiwanie po nazwie, kategorii i kraju — także po polsku
  („muzyka”, „dla dzieci”, „wiadomości”, „Niemcy”) oraz w pozostałych językach
  interfejsu.
- Odtwarzanie HLS z obsługą nagłówków `Referer` i `User-Agent`.
- Dodawanie i usuwanie własnych kanałów przez adres URL; źródła są zapisywane
  lokalnie. Obsługiwane są bezpośrednie strumienie HTTP/HTTPS oraz linki
  YouTube, Twitch, Rumble, Kick, Vimeo, Dailymotion i Odysee.
- Strumienie serwisów są rozwiązywane w tle przez `yt-dlp`; wymagane logowanie,
  materiały DRM i treści niedostępne publicznie nie są obsługiwane. Transmisje
  YouTube z osobnymi ścieżkami wideo i audio są odtwarzane razem; transmisje
  na żywo są ograniczone do maksymalnie 720p, aby ograniczyć buforowanie.
- **Tłumaczenie napisów na żywo** na język interfejsu — dla kanałów, które
  udostępniają napisy w strumieniu.
- **Nagrywanie bezstratne** (stream copy) z czerwonym przyciskiem i licznikiem
  czasu; pliki trafiają do `~/Wideo`, domyślnie AVI, z fallbackiem do MKV.
- EPG „teraz/potem” dla kanałów Pluto TV.
- 6 odświeżonych, lekkich motywów kolorystycznych, w tym fioletowy i
  kontrastowy; belka tytułowa dopasowuje się do wybranej skórki.
- Ulubione, głośność, motyw i język zapisywane lokalnie (`QSettings`).
- Cache bazy i logotypów — szybszy start i mniejsze zużycie sieci.
- Automatyczne pomijanie kanałów zamkniętych, NSFW i z listy blokad (DMCA).

## Napisy i tłumaczenie

Przycisk **💬 Napisy** włącza napisy kanału i tłumaczy je na aktualny język
interfejsu. Tłumaczenie pojawia się w dolnej części obrazu, a oryginalne napisy
pozostają ukryte.

Jak to działa:

1. libmpv wybiera pierwszą ścieżkę napisów dostępną w strumieniu (np. WebVTT).
2. Tekst kolejnych napisów jest wysyłany do endpointu Google Translate, a w
   razie niedostępności do MyMemory. Wyniki są buforowane w pamięci, a odpowiedź
   Google jest parsowana również wtedy, gdy zawiera wiele segmentów tekstu.
3. Wynik jest wyświetlany przez `osd-overlay`, więc nie zależy od formatowania
   napisów źródłowych.

Ograniczenia:

- Kanał musi **sam udostępniać napisy**. Aplikacja nie zawiera ASR i nie
  rozpoznaje mowy z obrazu.
- Nie są obsługiwane napisy obrazkowe (PGS/DVD) — potrzebny byłby OCR.
- Ścieżka napisów w HLS czasem pojawia się kilka sekund po starcie kanału.
- Publiczne endpointy tłumaczenia mogą mieć limity lub chwilowo nie działać.
- Wysyłany jest wyłącznie tekst napisów; nie są wysyłane dane konta ani obraz.

## Nagrywanie

Przycisk **⏺ Nagraj** zapisuje aktualnie odtwarzany kanał do pliku w katalogu
`~/Wideo` (lub `Videos`, jeśli taki istnieje). Nagrywanie:

- nie rekompresuje obrazu ani dźwięku (`ffmpeg -c copy`) — jakość jest taka
  sama jak w strumieniu źródłowym,
- domyślnie używa kontenera **AVI**,
- automatycznie ponawia zapis w **MKV**, jeśli AVI nie obsługuje kodeków
  strumienia,
- dla playlist HLS wybiera wariant o najwyższym `BANDWIDTH` (HD/FHD, jeśli
  nadawca go udostępnia),
- zatrzymuje się przyciskiem **⏹ Zatrzymaj zapis**, zmianie kanału, kliknięciu
  Stop lub zamknięciu aplikacji.
- podczas nagrywania wyświetla czerwony przycisk z aktualnym czasem zapisu.

Nagrywanie wymaga **FFmpeg**. Instalator Windows dołącza `ffmpeg.exe`;
uruchamianie ze źródeł na Windows wymaga FFmpeg w `PATH` lub obok aplikacji.
W Debianie i Fedorze FFmpeg jest zależnością pakietu. Nagrywanie działa dla
strumieni, które nie są zabezpieczone DRM i nie są geoblokowane. Pliki AVI z
kodekiem H.264/AAC odtwarza większość nowoczesnych odtwarzaczy; w razie
problemów użyj MKV (fallback) lub VLC/mpv.

## Obsługiwane formaty i kodeki

OmniTV nie implementuje własnych dekoderów — korzysta z libmpv/FFmpeg, więc
obsługa zależy od zainstalowanej wersji tych bibliotek.

| Warstwa    | Obsługa                                                           |
| ---------- | ----------------------------------------------------------------- |
| Kontenery  | HLS (`m3u8`), MP4, MKV, MPEG-TS, AVI, WebM, FLV                   |
| Wideo      | H.264/AVC, H.265/HEVC, AV1, VP9, VP8, MPEG-2, MPEG-4 Part 2, VC-1 |
| Dźwięk     | AAC, MP3, Opus, Vorbis, AC-3, E-AC-3, FLAC, MP2                   |
| Napisy     | WebVTT, SRT, ASS/SSA (tekstowe); napisy obrazkowe bez OCR         |
| Nagrywanie | strumień bez zmian (stream copy); AVI, a w razie potrzeby MKV     |

FFmpeg w wersji 6.0+ obsługuje większość współczesnych kodeków, w tym AV1,
HEVC, Opus i E-AC-3. Nagrywanie nie wymaga obecności enkoderów — wystarczy
demukser HLS i muxer AVI/MKV.

## Wymagania

- Python **3.10+** (testowane na 3.14) — tylko przy uruchamianiu ze źródeł.
- **libmpv** 2.x (Linux) lub `libmpv-2.dll` (Windows).
- **yt-dlp** (instalowane z `requirements.txt`) — do adresów stron serwisów
  streamingowych; bezpośrednie linki do strumieni nie wymagają resolvera.
- **FFmpeg** — wymagany do nagrywania; instalator Windows go dołącza, a pakiety
  Debian/Fedora deklarują go jako zależność systemową.
- Linux: X11 lub XWayland. Na Waylandzie aplikacja automatycznie wymusza
  `QT_QPA_PLATFORM=xcb`.
- Windows 10/11.

Testowane na Ubuntu 26.04 oraz na Fedorze (pakiet RPM, glibc >= 2.39) —
długotrwała praca bez problemów. Wersja bibliotek: PySide6 6.12,
python-mpv 1.0.8 i FFmpeg 8.0.

Po zbudowaniu pakiety instalacyjne są zapisywane w `dist/`:

- `omnity_0.2.0_amd64.deb` — Debian / Ubuntu,
- `omnity-0.2.0-*.x86_64.rpm` — Fedora,
- `OmniTV-Setup-0.2.0.exe` — Windows (budowany na Windows skryptem
  `packaging/windows/build.ps1`).

Skrypty pakujące generują sumy kontrolne SHA-256. Jeśli `dist/` zawiera pakiety
z wcześniejszej wersji, zbuduj je ponownie przed instalacją tej wersji.

## Instalacja — Debian / Ubuntu

### Pakiet .deb (zalecane)

```bash
sudo apt update
sudo apt install libmpv2 ffmpeg python3-venv
sudo apt install ./dist/omnity_0.2.0_amd64.deb
omnity
```

Pakiet sam deklaruje zależności `libc6 (>= 2.39)`, `libmpv2 | libmpv1`,
`ffmpeg` oraz biblioteki Qt/xcb. Jeśli `apt` zgłosi brak zależności:

```bash
sudo apt --fix-broken install
```

### Ze źródeł

```bash
cd OmniTV
./setup.sh
./run.sh
```

`setup.sh` tworzy `.venv`, instaluje zależności Pythona i sprawdza libmpv oraz
FFmpeg. Ręcznie:

```bash
sudo apt install libmpv2 ffmpeg python3-venv
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m omnity.main
```

## Instalacja — Fedora

### Pakiet RPM (zalecane)

```bash
sudo dnf install ./dist/omnity-0.2.0-*.x86_64.rpm
omnity
```

Pakiet instaluje aplikację w `/usr/lib64/omnity`, dowiązanie `omnity` w
`/usr/bin`, ikonę i plik `.desktop`. Wymaga `mpv-libs`, `ffmpeg` oraz bibliotek
xcb/xkbcommon. Pakiet nie jest podpisany — `dnf` może poprosić o potwierdzenie. Jeśli `ffmpeg` nie jest dostępny w oficjalnym repozytorium, włącz
RPM Fusion:

```bash
sudo dnf install https://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm
sudo dnf install ffmpeg
```

> Pakiety Linux wymagają glibc >= 2.39 (Ubuntu 24.04+, Debian 13+, Fedora 40+).
> Bundle jest budowany z PyInstallera; skrypty pakujące automatycznie obniżają
> wymagania wybranych funkcji libc/libm do `GLIBC_2.2.5`, jeśli budowa odbyła
> się na nowszym systemie (np. z glibc 2.44). Dzięki temu ten sam pakiet działa
> na starszych dystrybucjach. Do w pełni natywnego pakietu zbuduj go na Fedorze:
> `bash packaging/fedora/build_rpm.sh`.

### Ze źródeł

```bash
sudo dnf install mpv-libs python3 python3-pip ffmpeg libxcb libxkbcommon-x11
cd OmniTV
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m omnity.main
```

## Instalacja — Windows

### Instalator

Użyj instalatora `dist\OmniTV-Setup-0.2.0.exe` z wydań projektu albo pobierz go
z artefaktu workflow GitHub Actions (patrz „Windows — GitHub Actions”). Możesz
też zbudować go sam na Windows (patrz „Pakowanie”). Instalator zawiera aplikację,
biblioteki Pythona/Qt, `libmpv-2.dll` i `ffmpeg.exe` do nagrywania. Nie da się
go zbudować na Linuksie, ponieważ PyInstaller i Inno Setup działają tylko na
Windows.

Przy uruchamianiu przenośnej kopii `OmniTV.exe` poza instalatorem wymagane są
obok niego:

- `libmpv-2.dll` — biblioteka odtwarzacza (np. z
  <https://sourceforge.net/projects/mpv-player-windows/files/libmpv/>),
- `ffmpeg.exe` — potrzebny do nagrywania; pobierz np. z
  <https://www.gyan.dev/ffmpeg/builds/> i skopiuj obok `OmniTV.exe` (albo dodaj
  FFmpeg do `PATH`).

### Ze źródeł

```powershell
cd OmniTV
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m omnity.main
```

Zainstaluj wcześniej Python 3.13 x64 i zaznacz dodanie go do `PATH` (wraz z
launcherem `py`). Pliki `libmpv-2.dll` oraz `ffmpeg.exe` umieść w katalogu
projektu lub zapewnij ich dostępność przez `PATH`. Instalator nie jest podpisany
certyfikatem — Windows SmartScreen może poprosić o potwierdzenie.

## Język, motywy i sterowanie

- **Język** wybiera się listą w lewym panelu. Przy pierwszym uruchomieniu
  aplikacja próbuje użyć języka systemowego, a domyślnie wybiera polski.
- **Motyw** wybiera się listą w lewym panelu: Ciemny, Jasny, Nocny błękit,
  Leśny, Kontrast, Fiolet. Belka tytułowa zmienia kolor razem z motywem.
- **Własny kanał / stream** dodasz przyciskiem pod listą kanałów. Wklej adres
  HTTP/HTTPS i nazwę. Aby usunąć własny wpis, zaznacz go i wybierz **Usuń
  własny**. Direct streamy są odtwarzane przez libmpv, a linki obsługiwanych
  serwisów przez yt-dlp; dostęp zależy od publicznych możliwości serwisu.
- Podczas nagrywania czerwony przycisk pokazuje czas nagrania; kliknij go, aby
  zatrzymać zapis.
- **F11** — pełny ekran; **Esc** — wyjście z pełnego ekranu.
- Okno można przesuwać, chwytając belkę tytułową, a rozmiar zmieniać uchwytem
  w prawym dolnym rogu. Dwuklik na belce maksymalizuje/przywraca okno.

Ustawienia są przechowywane w `QSettings`:

- Linux: `~/.config/OmniTV/OmniTV.conf`
- Windows: rejestr użytkownika (`HKCU\Software\OmniTV\OmniTV`)

## Cache i dane

- Baza kanałów, logotypy i EPG: `~/.local/share/omnity/cache` (Linux) lub
  `%LOCALAPPDATA%\omnity\cache` (Windows).
- Nagrania: `~/Wideo` (Linux) lub `%USERPROFILE%\Videos` (Windows).
- Własne kanały: lokalne ustawienia użytkownika (`QSettings`), bez synchronizacji.
- Przycisk **Odśwież bazę kanałów** wymusza ponowne pobranie danych.

## Rozwiązywanie problemów

- **Czarny obraz na Waylandzie** — libmpv jest osadzany przez X11. Aplikacja i
  `run.sh` automatycznie ustawiają `QT_QPA_PLATFORM=xcb` w sesji Wayland.
  Ręcznie: `QT_QPA_PLATFORM=xcb omnity`.
- **Zacięcia na słabym komputerze / VM** — domyślnie używany jest stabilny
  `vo=x11` i dekodowanie software'owe. Można dostroić:
  - `OMNITY_CACHE_SECS=8` — mniejsze opóźnienie,
  - `OMNITY_CACHE_SECS=25` — większa płynność,
  - `OMNITY_HLS_BITRATE=min` — najniższy wariant HLS,
  - `OMNITY_THREADS=2` — mniej wątków dekodera,
  - `OMNITY_HWDEC=auto` — spróbuj dekodowania sprzętowego,
  - `OMNITY_VO=gpu` — eksperymentalny renderer GPU (może crashować na VM).
- **„libmpv niedostępny” / `Failed to load dynlib/dll 'libmpv.so.2'`** —
  `python-mpv` jest częścią aplikacji, ale systemowa biblioteka libmpv musi być
  zainstalowana osobno. Na Ubuntu/Debian uruchom
  `sudo apt update && sudo apt install libmpv2` (na starszych wydaniach może to
  być `libmpv1`), a następnie `sudo apt --fix-broken install`, jeśli pakiet
  OmniTV był instalowany przez `dpkg -i`. Sprawdź dostępność biblioteki przez
  `ldconfig -p | grep libmpv.so.2`. W Fedorze użyj `sudo dnf install mpv-libs`;
  w Windows umieść `libmpv-2.dll` obok aplikacji.
- **Błąd `undefined symbol ... HOGWEED` lub `vaMapBuffer2` przy ładowaniu
  libmpv** — starszy pakiet mógł zawierać kopie bibliotek kryptograficznych
  albo VA-API niezgodne z bibliotekami systemu. Pobierz i zainstaluj ponownie
  aktualny pakiet Linux, który używa systemowych Nettle/Hogweed i VA-API.
- **Nagrywanie nie startuje** — sprawdź `ffmpeg -version`; w Debianie/Ubuntu
  `sudo apt install ffmpeg`, w Fedorze `sudo dnf install ffmpeg`. Sprawdź też
  wolne miejsce na dysku i czy kanał nie jest geoblokowany.
- **Link do serwisu streamingowego nie działa** — zaktualizuj `yt-dlp`
  (`pip install --upgrade yt-dlp`) przy uruchamianiu ze źródeł. Materiały
  wymagające logowania, DRM lub niedostępne publicznie mogą nie być obsługiwane.
- **Zapis AVI nie odtwarza się** — aplikacja powinna automatycznie przejść na
  MKV. Jeśli nie, użyj VLC/mpv; AVI nie jest idealnym kontenerem dla wszystkich
  współczesnych kodeków.
- **Brak napisów** — kanał może nie mieć napisów, ścieżka może pojawić się po
  kilku sekundach albo serwis tłumaczenia jest chwilowo niedostępny. Spróbuj
  ponownie włączyć przycisk napisów.
- **Kanał nie działa** — publiczne strumienie bywają niestabilne, geoblokowane
  lub wyłączone. Spróbuj innego kanału lub odśwież bazę.
- **Diagnostyka** — `omnity --selftest` sprawdza PySide6, libmpv i ikonę;
  `omnity --selftest-mpv` testuje backend libmpv; `omnity --playtest <id>`
  odtwarza kanał przez 20 s i wypisuje stan.

## Pakowanie

### Debian / Ubuntu (.deb)

```bash
.venv/bin/pip install pyinstaller
bash packaging/linux/build_deb.sh
sudo apt install ./dist/omnity_0.2.0_amd64.deb
```

Skrypt używa PyInstallera z `.venv`, buduje aplikację do `build/linux-dist`
(bez nadpisywania windowsowego `dist/OmniTV`), składa drzewo pakietu i tworzy
`.deb` w `dist/` wraz z plikiem `.sha256`. Pakiet zależy od `libc6 (>= 2.39)`,
`libmpv2 | libmpv1`, `ffmpeg` oraz bibliotek Qt/xcb. Ikona trafia do menu
systemowego. Po zbudowaniu bundle jest sprawdzany przez
`packaging/linux/fix_glibc_compat.py`, który obniża wymagania glibc wybranych
funkcji libc/libm do `GLIBC_2.2.5`, aby pakiet działał na glibc 2.39.

Jeśli bundle został już zbudowany i chcesz tylko odtworzyć pakiet, użyj
`SKIP_BUILD=1 bash packaging/linux/build_deb.sh`.

### Fedora (.rpm)

```bash
sudo dnf install rpm-build
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt pyinstaller
bash packaging/fedora/build_rpm.sh
sudo dnf install ./dist/omnity-0.2.0-*.x86_64.rpm
```

Skrypt buduje bundle PyInstaller w `build/linux-dist`, stosuje tę samą korektę
zgodności glibc, pakuje go do RPM i zapisuje wynik w `dist/` razem z plikiem
`.sha256`. Specyfikacja jest w `packaging/fedora/omnity.spec`. RPM można też
zbudować na Ubuntu/Debian po wskazaniu `rpmbuild` przez
`RPMBUILD=/ścieżka/do/rpmbuild`. Skrypt działa również, gdy ścieżka projektu
zawiera spacje (używa dowiązania pod ścieżką bez spacji). W przypadku gotowego
bundla użyj `SKIP_BUILD=1 bash packaging/fedora/build_rpm.sh`.

### Debian / Ubuntu i Fedora — GitHub Actions

Workflow `.github/workflows/linux-packages.yml` buduje oba pakiety na Ubuntu
24.04. Prześlij zawartość folderu `Github transfer` do repozytorium GitHub, a
następnie wybierz **Actions → Linux packages → Run workflow**. Gotowe pliki
`.deb` i `.rpm` (wraz z sumami `.sha256`) pobierzesz z artefaktów zakończonego
uruchomienia. Workflow uruchamia testy przed pakowaniem; instalator RPM wymaga
glibc 2.39 lub nowszej.

### Windows (instalator .exe)

```powershell
powershell -ExecutionPolicy Bypass -File packaging\windows\build.ps1
```

Skrypt instaluje PyInstallera, buduje `dist\OmniTV\OmniTV.exe`, kopiuje
`libmpv-2.dll` i dołącza `ffmpeg.exe`. Jeśli FFmpeg nie znajduje się w projekcie
ani w `PATH`, skrypt pobiera wydanie essentials z gyan.dev. Następnie — gdy
zainstalowany jest [Inno Setup 6](https://jrsoftware.org/isinfo.php) —
automatycznie tworzy `dist\OmniTV-Setup-0.2.0.exe` zawierający wymagane pliki.
Bez Inno Setup otwórz `packaging/windows/installer.iss` i skompiluj ręcznie.

> PyInstaller nie kompiluje krzyżowo: `.deb` i `.rpm` buduj na Linuksie, `.exe`
> na Windows.

### Windows — GitHub Actions

Workflow `.github/workflows/windows-installer.yml` buduje instalator na
`windows-latest`. Uruchom go ręcznie w zakładce **Actions → Windows installer →
Run workflow** albo wypchnij tag `v*`. Workflow:

1. instaluje Pythona, PyInstallera i Inno Setup,
2. pobiera najnowszy `libmpv-2.dll` z wydań `shinchiro/mpv-winbuild-cmake`,
3. pobiera FFmpeg essentials z gyan.dev,
4. buduje aplikację i `OmniTV-Setup-0.2.0.exe`,
5. publikuje artefakt `OmniTV-Setup-windows-x64` wraz z sumą SHA-256.

Gotowy plik pobierzesz z podsumowania uruchomienia workflow. Instalator nie jest
podpisany certyfikatem, więc SmartScreen może poprosić o potwierdzenie.

## Struktura projektu

```
OmniTV/
├── omnity/
│   ├── main.py                 # punkt wejścia i testy diagnostyczne
│   ├── i18n.py                 # tłumaczenia interfejsu
│   ├── countries_i18n.py       # nazwy krajów w 7 językach
│   ├── core/
│   │   ├── catalog.py          # baza iptv-org, cache, wybór strumienia
│   │   └── epg.py              # źródła i parsowanie XMLTV
│   └── ui/
│       ├── main_window.py      # okno, filtry, napisy, nagrywanie
│       ├── player_widget.py    # libmpv, napisy i overlay
│       ├── subtitles.py        # tłumaczenie napisów
│       ├── recorder.py         # nagrywanie FFmpeg (AVI/MKV)
│       ├── stream_resolver.py  # obsługa linków serwisów przez yt-dlp
│       ├── title_bar.py        # belka tytułowa dopasowana do motywu
│       ├── loader.py           # wątek pobierania bazy
│       ├── logo_loader.py      # asynchroniczne logotypy
│       ├── epg_worker.py       # wątek EPG
│       └── themes.py           # motywy QSS
├── tests/
│   └── test_stream_features.py # testy adresów, flag i odpowiedzi tłumaczenia
├── .github/workflows/
│   ├── linux-packages.yml      # pakiety Debian/Fedora w GitHub Actions
│   └── windows-installer.yml   # instalator Windows w GitHub Actions
├── packaging/
│   ├── omnity.spec             # konfiguracja PyInstaller
│   ├── linux/{build_deb.sh, fix_glibc_compat.py}
│   ├── fedora/{build_rpm.sh, omnity.spec}
│   └── windows/{build.ps1, installer.iss, omnity.ico}
├── requirements.txt
├── LICENSE
├── setup.sh
└── run.sh
```

Testy uruchomisz ze środowiska zainstalowanego z `requirements.txt`:

```powershell
cd OmniTV
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

## Licencja

OmniTV jest udostępniane na warunkach GNU General Public License v3.0
(`GPL-3.0-only`). Pełny tekst znajduje się w pliku `LICENSE`.

## Prywatność i aspekt prawny

OmniTV jest tylko odtwarzaczem — nie hostuje ani nie dostarcza treści. Korzysta
z publicznie dostępnych strumieni zgromadzonych przez iptv-org. Respektuj prawo
lokalne oraz warunki korzystania nadawców. Aplikacja domyślnie pomija kanały z
listy blokad i oznaczone jako NSFW.

Tekst napisów jest wysyłany do zewnętrznego serwisu tłumaczeniowego tylko po
włączeniu tłumaczenia. Ustawienia, ulubione i cache pozostają lokalnie; aplikacja
nie wymaga konta ani logowania.

## EPG — zakres i ograniczenia

Publiczne API iptv-org nie zawiera już adresów przewodników (`guides.json` ma
puste `sources`). Dlatego EPG jest realizowane dla kanałów **Pluto TV** z
publicznych feedów XMLTV `i.mjh.nz` (per region). Dla pozostałych kanałów panel
pokazuje „brak danych EPG”. Dopasowanie programu odbywa się po nazwie kanału.

## Pomysły na dalszy rozwój

- „Ostatnio oglądane”.
- Wybór jakości i alternatywnego strumienia dla kanału.
- EPG dla kolejnych dostawców (Samsung TV Plus, Plex) lub własny plik XMLTV.
- Automatyczna aktualizacja bazy w tle.
- Opcjonalny wybór ścieżki napisów i języka źródłowego.

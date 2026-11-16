"""Główne okno OmniTV: filtry, ulubione, lista kanałów, EPG i sterowanie."""

from __future__ import annotations

import os
import re
import time
import unicodedata
from datetime import datetime
from urllib.parse import urlsplit
from uuid import uuid4

from PySide6.QtCore import QEvent, QLocale, QSettings, QSize, Qt, QTimer
from PySide6.QtGui import QGuiApplication, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizeGrip,
    QSlider,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from omnity.core.epg import sources_for_channel
from omnity.i18n import (
    CATEGORY_NAMES,
    COUNTRY_NAMES,
    DEFAULT_LANGUAGE,
    LANGUAGES,
    LANGUAGE_CODES,
    category_name,
    country_name,
    current_language,
    set_language,
    theme_name,
    tr,
)
from omnity.ui.epg_worker import EpgWorker
from omnity.ui.loader import CatalogLoader
from omnity.ui.logo_loader import LogoLoader
from omnity.ui.player_widget import PlayerWidget
from omnity.ui.recorder import Recorder
from omnity.ui.subtitles import SubtitleTranslator
from omnity.ui.stream_resolver import StreamResolver, requires_resolution
from omnity.ui.themes import DEFAULT_THEME, build_stylesheet, theme_names
from omnity.ui.title_bar import TitleBar

MAX_RESULTS = 2000
MAX_LOGO_ITEMS = 300

SEARCH_SYNONYMS = {
    "muzyka": "music",
    "muzyki": "music",
    "muzyczny": "music",
    "muzyczne": "music",
    "muzyczna": "music",
    "film": "movies",
    "filmy": "movies",
    "filmowy": "movies",
    "filmowe": "movies",
    "filmowa": "movies",
    "wiadomosci": "news",
    "informacje": "news",
    "informacyjne": "news",
    "sport": "sports",
    "sportowy": "sports",
    "sportowe": "sports",
    "sportowa": "sports",
    "dzieci": "kids",
    "dziecko": "kids",
    "dzieciece": "kids",
    "dla dzieci": "kids",
    "dokument": "documentary",
    "dokumenty": "documentary",
    "dokumentalny": "documentary",
    "dokumentalne": "documentary",
    "rozrywka": "entertainment",
    "rozrywkowe": "entertainment",
    "serial": "series",
    "seriale": "series",
    "serialowe": "series",
    "gotowanie": "cooking",
    "kuchnia": "cooking",
    "podroze": "travel",
    "podroz": "travel",
    "pogoda": "weather",
    "nauka": "science",
    "religia": "religious",
    "religijny": "religious",
    "kultura": "culture",
    "biznes": "business",
    "rodzina": "family",
    "familijny": "family",
    "animacja": "animation",
    "animowany": "animation",
    "klasyka": "classic",
    "komedia": "comedy",
    "zakupy": "shop",
    "sklep": "shop",
    "polska": "poland",
    "niemcy": "germany",
    "francja": "france",
    "hiszpania": "spain",
    "wlochy": "italy",
    "rosja": "russia",
    "ukraina": "ukraine",
    "czechy": "czechia",
    "usa": "united states",
    "ameryka": "united states",
    "anglia": "united kingdom",
    "wielka brytania": "united kingdom",
}

# Angielski (dodatkowe synonimy kategorii).
SEARCH_SYNONYMS.update(
    {
        "films": "movies",
        "cinema": "movies",
        "children": "kids",
        "cartoons": "animation",
        "cartoon": "animation",
        "shows": "series",
        "information": "news",
        "cars": "auto",
        "nature": "outdoor",
        "relaxation": "relax",
        "religion": "religious",
        "shopping": "shop",
    }
)

# Niemiecki.
SEARCH_SYNONYMS.update(
    {
        "musik": "music",
        "filme": "movies",
        "nachrichten": "news",
        "kinder": "kids",
        "dokumentation": "documentary",
        "dokumentarfilm": "documentary",
        "unterhaltung": "entertainment",
        "serie": "series",
        "serien": "series",
        "komodie": "comedy",
        "reisen": "travel",
        "wetter": "weather",
        "wissenschaft": "science",
        "religios": "religious",
        "kultur": "culture",
        "wirtschaft": "business",
        "geschaft": "business",
        "familie": "family",
        "zeichentrick": "animation",
        "kochen": "cooking",
        "kuche": "cooking",
        "einkaufen": "shop",
        "klassiker": "classic",
        "bildung": "education",
        "lebensstil": "lifestyle",
        "offentlich": "public",
        "entspannung": "relax",
        "drausen": "outdoor",
        "natur": "outdoor",
        "interaktiv": "interactive",
        "gesetzgebung": "legislative",
        "allgemein": "general",
        "deutschland": "germany",
        "polen": "poland",
        "frankreich": "france",
        "spanien": "spain",
        "italien": "italy",
        "russland": "russia",
        "osterreich": "austria",
        "schweiz": "switzerland",
        "vereinigte staaten": "united states",
        "grossbritannien": "united kingdom",
    }
)

# Rosyjski.
SEARCH_SYNONYMS.update(
    {
        "музыка": "music",
        "фильмы": "movies",
        "кино": "movies",
        "новости": "news",
        "спорт": "sports",
        "дети": "kids",
        "детский": "kids",
        "документальный": "documentary",
        "документальные": "documentary",
        "развлечения": "entertainment",
        "сериал": "series",
        "сериалы": "series",
        "комедия": "comedy",
        "путешествия": "travel",
        "погода": "weather",
        "наука": "science",
        "религия": "religious",
        "религиозный": "religious",
        "культура": "culture",
        "бизнес": "business",
        "семья": "family",
        "анимация": "animation",
        "мультфильмы": "animation",
        "кулинария": "cooking",
        "готовка": "cooking",
        "покупки": "shop",
        "магазин": "shop",
        "классика": "classic",
        "образование": "education",
        "образ жизни": "lifestyle",
        "авто": "auto",
        "автомобили": "auto",
        "общественный": "public",
        "общие": "general",
        "общий": "general",
        "расслабление": "relax",
        "релакс": "relax",
        "природа": "outdoor",
        "открытый воздух": "outdoor",
        "интерактивный": "interactive",
        "законодательный": "legislative",
        "германия": "germany",
        "польша": "poland",
        "франция": "france",
        "испания": "spain",
        "италия": "italy",
        "россия": "russia",
        "украина": "ukraine",
        "сша": "united states",
        "великобритания": "united kingdom",
        "австрия": "austria",
        "швейцария": "switzerland",
    }
)

# Francuski.
SEARCH_SYNONYMS.update(
    {
        "musique": "music",
        "actualites": "news",
        "infos": "news",
        "nouvelles": "news",
        "enfants": "kids",
        "documentaire": "documentary",
        "divertissement": "entertainment",
        "series": "series",
        "comedie": "comedy",
        "voyage": "travel",
        "voyages": "travel",
        "meteo": "weather",
        "religieux": "religious",
        "affaires": "business",
        "entreprise": "business",
        "famille": "family",
        "dessins animes": "animation",
        "dessin anime": "animation",
        "cuisine": "cooking",
        "achats": "shop",
        "boutique": "shop",
        "classique": "classic",
        "mode de vie": "lifestyle",
        "automobile": "auto",
        "detente": "relax",
        "plein air": "outdoor",
        "interactif": "interactive",
        "legislatif": "legislative",
        "allemagne": "germany",
        "pologne": "poland",
        "espagne": "spain",
        "italie": "italy",
        "russie": "russia",
        "etats-unis": "united states",
        "etats unis": "united states",
        "royaume-uni": "united kingdom",
        "royaume uni": "united kingdom",
        "autriche": "austria",
        "suisse": "switzerland",
    }
)

# Włoski.
SEARCH_SYNONYMS.update(
    {
        "musica": "music",
        "notizie": "news",
        "bambini": "kids",
        "documentario": "documentary",
        "intrattenimento": "entertainment",
        "commedia": "comedy",
        "viaggi": "travel",
        "viaggio": "travel",
        "scienza": "science",
        "religione": "religious",
        "religioso": "religious",
        "cultura": "culture",
        "affari": "business",
        "impresa": "business",
        "famiglia": "family",
        "animazione": "animation",
        "cartoni animati": "animation",
        "cucina": "cooking",
        "acquisti": "shop",
        "negozio": "shop",
        "classico": "classic",
        "istruzione": "education",
        "educazione": "education",
        "stile di vita": "lifestyle",
        "pubblico": "public",
        "all'aperto": "outdoor",
        "all aperto": "outdoor",
        "natura": "outdoor",
        "interattivo": "interactive",
        "legislativo": "legislative",
        "generale": "general",
        "germania": "germany",
        "polonia": "poland",
        "francia": "france",
        "spagna": "spain",
        "italia": "italy",
        "russia": "russia",
        "ucraina": "ukraine",
        "stati uniti": "united states",
        "regno unito": "united kingdom",
        "austria": "austria",
        "svizzera": "switzerland",
    }
)

# Hiszpański.
SEARCH_SYNONYMS.update(
    {
        "peliculas": "movies",
        "pelicula": "movies",
        "cine": "movies",
        "noticias": "news",
        "deportes": "sports",
        "ninos": "kids",
        "documental": "documentary",
        "entretenimiento": "entertainment",
        "comedia": "comedy",
        "viajes": "travel",
        "viaje": "travel",
        "clima": "weather",
        "tiempo": "weather",
        "ciencia": "science",
        "cultura": "culture",
        "negocios": "business",
        "empresa": "business",
        "familia": "family",
        "animacion": "animation",
        "dibujos animados": "animation",
        "cocina": "cooking",
        "compras": "shop",
        "tienda": "shop",
        "clasico": "classic",
        "educacion": "education",
        "estilo de vida": "lifestyle",
        "coche": "auto",
        "automovil": "auto",
        "publico": "public",
        "relajacion": "relax",
        "aire libre": "outdoor",
        "naturaleza": "outdoor",
        "interactivo": "interactive",
        "legislativo": "legislative",
        "general": "general",
        "alemania": "germany",
        "espana": "spain",
        "rusia": "russia",
        "ucrania": "ukraine",
        "estados unidos": "united states",
        "reino unido": "united kingdom",
        "suiza": "switzerland",
    }
)


def _normalize(value: str) -> str:
    value = (value or "").translate(
        str.maketrans(
            {
                "ł": "l",
                "Ł": "L",
                "ø": "o",
                "Ø": "O",
                "đ": "d",
                "Đ": "D",
                "ß": "ss",
                "œ": "oe",
                "Œ": "Oe",
                "æ": "ae",
                "Æ": "Ae",
            }
        )
    )
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return " ".join(value.lower().split())


SEARCH_STOPWORDS = {
    "a", "and", "dla", "do", "i", "in", "kanal", "kanaly", "na", "o", "od",
    "of", "on", "stacja", "stacje", "the", "w", "we", "z", "ze",
    # angielski / niemiecki / francuski
    "for", "with", "der", "die", "das", "und", "fur", "von", "im", "den",
    "dem", "ein", "eine", "les", "la", "le", "et", "des", "du", "de", "pour",
    "avec", "une", "un", "chaine", "chaines", "sender",
    # hiszpański / włoski
    "el", "los", "las", "y", "del", "para", "con", "uno", "una", "il", "lo",
    "gli", "e", "di", "della", "dei", "per", "canal", "canales", "canale",
    "canali",
    # rosyjski
    "и", "в", "на", "для", "с", "по", "из", "о", "канал", "каналы",
}

SEARCH_SYNONYMS.update(
    {
        "musical": "music",
        "musicale": "music",
        "musicales": "music",
        "musicali": "music",
        "музыкальный": "music",
        "музыкальные": "music",
        "sportive": "sports",
        "sportives": "sports",
        "sportivi": "sports",
        "deportivo": "sports",
        "deportivos": "sports",
        "спортивные": "sports",
        "documentaires": "documentary",
        "documentales": "documentary",
        "documentari": "documentary",
        "informativos": "news",
        "informative": "news",
    }
)


def _expand_query(text: str) -> list[str]:
    normalized = _normalize(text)
    if not normalized:
        return []
    if normalized in SEARCH_SYNONYMS:
        return [SEARCH_SYNONYMS[normalized]]
    tokens = [
        SEARCH_SYNONYMS.get(token, token)
        for token in normalized.split()
        if token not in SEARCH_STOPWORDS
    ]
    return list(dict.fromkeys(tokens))


def _token_matches(token: str, blob: str) -> bool:
    if len(token) <= 3:
        return re.search(rf"\b{re.escape(token)}\b", blob) is not None
    return token in blob


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        screen = QGuiApplication.primaryScreen()
        if screen is not None:
            available = screen.availableGeometry()
            minimum_width = min(900, available.width())
            minimum_height = min(520, available.height())
            self.setMinimumSize(minimum_width, minimum_height)
            self.resize(
                max(minimum_width, min(1200, available.width() - 32)),
                max(minimum_height, min(720, available.height() - 32)),
            )
            self.move(
                available.center().x() - self.width() // 2,
                available.center().y() - self.height() // 2,
            )
        else:
            self.setMinimumSize(900, 520)
            self.resize(1200, 720)

        self._catalog = None
        self._loader = None
        self._channels = []
        self._favorites: set[str] = set()
        self._item_by_channel: dict[str, QListWidgetItem] = {}
        self._search_blob: dict[str, str] = {}
        self._search_tokens: list[str] = []
        self._current_channel_id = None
        self._current_channel_name = ""
        self._epg_worker = None
        self._epg_loading = False
        self._epg_programmes = None
        self._load_failed = False
        self._loading_force = False
        self._closing = False
        self._subtitle_enabled = False
        self._subtitle_wait_started = 0.0
        self._subtitle_last_text = ""
        self._subtitle_request = 0
        self._recording_path = ""
        self._recording_started_at = 0.0
        self._current_stream = None
        self._stream_request_id = 0
        self._stream_resolvers = []
        self._close_pending = False
        self._settings = QSettings("OmniTV", "OmniTV")
        self._custom_channels = self._load_custom_channels()

        saved_language = self._settings.value("language", "", type=str)
        if saved_language not in LANGUAGE_CODES:
            system_language = QLocale.system().name().split("_")[0]
            saved_language = (
                system_language
                if system_language in LANGUAGE_CODES
                else DEFAULT_LANGUAGE
            )
        set_language(saved_language)
        self.setWindowTitle(tr("app_title"))

        self._logo_loader = LogoLoader(self)
        self._logo_loader.icon_ready.connect(self._on_logo_ready)

        self._subtitle_translator = SubtitleTranslator(self)
        self._subtitle_translator.translated.connect(self._on_subtitle_translated)
        self._subtitle_translator.failed.connect(self._on_subtitle_failed)
        self._subtitle_timer = QTimer(self)
        self._subtitle_timer.setInterval(250)
        self._subtitle_timer.timeout.connect(self._poll_subtitles)

        self._recorder = Recorder(self)
        self._recorder.started.connect(self._on_recording_started)
        self._recorder.stopped.connect(self._on_recording_stopped)
        self._recorder.failed.connect(self._on_recording_failed)
        self._recorder.fallback.connect(self._on_recording_fallback)
        self._record_timer = QTimer(self)
        self._record_timer.setInterval(1000)
        self._record_timer.timeout.connect(self._update_record_button)

        self._build_ui()
        self._restore_state()
        self._start_loading(force=False)

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self._title_bar = TitleBar(self)
        outer.addWidget(self._title_bar)

        content = QWidget()
        outer.addWidget(content, 1)
        root = QHBoxLayout(content)
        root.setContentsMargins(8, 8, 8, 8)

        self._splitter = QSplitter(Qt.Horizontal)
        root.addWidget(self._splitter)

        self._size_grip = QSizeGrip(self)
        self._size_grip.setFixedSize(18, 18)
        self._size_grip.raise_()

        # --- panel lewy ---
        self._left = QWidget()
        left = QVBoxLayout(self._left)
        left.setContentsMargins(2, 2, 8, 2)
        left.setSpacing(10)

        language_row = QHBoxLayout()
        self._language_label = QLabel(tr("language_label"))
        language_row.addWidget(self._language_label)
        self._language = QComboBox()
        for code, native_name in LANGUAGES:
            self._language.addItem(native_name, code)
        self._language.currentIndexChanged.connect(self._on_language_changed)
        language_row.addWidget(self._language, 1)
        left.addLayout(language_row)

        theme_row = QHBoxLayout()
        self._theme_label = QLabel(tr("theme_label"))
        theme_row.addWidget(self._theme_label)
        self._theme = QComboBox()
        for key in theme_names():
            self._theme.addItem(theme_name(key), key)
        self._theme.currentIndexChanged.connect(self._on_theme_changed)
        theme_row.addWidget(self._theme, 1)
        left.addLayout(theme_row)

        self._search = QLineEdit()
        self._search.setPlaceholderText(tr("search_placeholder"))
        self._search.textChanged.connect(self._apply_filters)
        left.addWidget(self._search)

        self._country = QComboBox()
        self._country.setToolTip(tr("country_filter"))
        self._country.currentIndexChanged.connect(self._apply_filters)
        left.addWidget(self._country)

        self._category = QComboBox()
        self._category.setToolTip(tr("category_filter"))
        self._category.currentIndexChanged.connect(self._apply_filters)
        left.addWidget(self._category)

        favorite_row = QHBoxLayout()
        self._fav_btn = QPushButton(tr("add_favorite"))
        self._fav_btn.clicked.connect(self._toggle_favorite)
        favorite_row.addWidget(self._fav_btn, 1)
        self._only_favorites = QCheckBox(tr("only_favorites"))
        self._only_favorites.toggled.connect(self._apply_filters)
        favorite_row.addWidget(self._only_favorites)
        left.addLayout(favorite_row)

        self._count = QLabel(tr("loading_db"))
        self._count.setObjectName("hint")
        left.addWidget(self._count)

        self._list = QListWidget()
        self._list.setAlternatingRowColors(True)
        self._list.setIconSize(QSize(24, 24))
        self._list.itemActivated.connect(self._on_item_activated)
        self._list.currentItemChanged.connect(self._update_fav_button)
        left.addWidget(self._list, 1)

        source_row = QHBoxLayout()
        self._add_source_btn = QPushButton(tr("add_custom_channel"))
        self._add_source_btn.clicked.connect(self._add_custom_channel)
        source_row.addWidget(self._add_source_btn, 1)
        self._remove_source_btn = QPushButton(tr("remove_custom_channel"))
        self._remove_source_btn.clicked.connect(self._remove_custom_channel)
        self._remove_source_btn.setEnabled(False)
        source_row.addWidget(self._remove_source_btn)
        left.addLayout(source_row)

        self._refresh = QPushButton(tr("refresh_db"))
        self._refresh.clicked.connect(lambda: self._start_loading(force=True))
        left.addWidget(self._refresh)

        self._left.setMinimumWidth(300)
        self._left.setMaximumWidth(460)
        self._splitter.addWidget(self._left)

        # --- panel prawy ---
        self._right = QWidget()
        right = QVBoxLayout(self._right)
        right.setContentsMargins(0, 0, 0, 0)
        right.setSpacing(10)

        self._player = PlayerWidget()
        self._player.setObjectName("playerWidget")
        right.addWidget(self._player, 1)

        self._now = QLabel(tr("no_channel"))
        self._now.setObjectName("nowPlaying")
        right.addWidget(self._now)

        self._epg = QLabel(tr("epg_prefix"))
        self._epg.setObjectName("epgLabel")
        self._epg.setWordWrap(True)
        self._epg.setTextInteractionFlags(Qt.TextSelectableByMouse)
        right.addWidget(self._epg)

        controls = QHBoxLayout()

        self._play_btn = QPushButton(tr("play"))
        self._play_btn.clicked.connect(self._play_selected)
        controls.addWidget(self._play_btn)

        self._pause_btn = QPushButton(tr("pause"))
        self._pause_btn.clicked.connect(self._player.toggle_pause)
        controls.addWidget(self._pause_btn)

        self._stop_btn = QPushButton(tr("stop"))
        self._stop_btn.clicked.connect(self._stop)
        controls.addWidget(self._stop_btn)

        self._mute_btn = QPushButton("🔊")
        self._mute_btn.setFixedWidth(40)
        self._mute_btn.setToolTip(tr("mute"))
        self._mute_btn.clicked.connect(self._toggle_mute)
        controls.addWidget(self._mute_btn)

        self._subs_btn = QPushButton(tr("subtitles_off"))
        self._subs_btn.setCheckable(True)
        self._subs_btn.setToolTip(tr("subtitles_off"))
        self._subs_btn.clicked.connect(self._toggle_subtitles)

        self._record_btn = QPushButton(tr("record"))
        self._record_btn.setObjectName("recordButton")
        self._record_btn.clicked.connect(self._toggle_recording)

        controls.addStretch(1)

        self._volume_label = QLabel(tr("volume"))
        self._volume = QSlider(Qt.Horizontal)
        self._volume.setRange(0, 100)
        self._volume.setValue(70)
        self._volume.setFixedWidth(140)
        self._volume.valueChanged.connect(self._on_volume)

        self._fullscreen_btn = QPushButton(tr("fullscreen"))
        self._play_btn.setObjectName("primaryButton")
        self._fullscreen_btn.clicked.connect(self._toggle_fullscreen)
        controls.addWidget(self._fullscreen_btn)
        right.addLayout(controls)

        extras = QHBoxLayout()
        extras.addWidget(self._subs_btn)
        extras.addWidget(self._record_btn)
        extras.addWidget(self._volume_label)
        extras.addWidget(self._volume)
        extras.addStretch(1)
        right.addLayout(extras)

        self._subs_status = QLabel("")
        self._subs_status.setObjectName("hint")
        self._subs_status.setWordWrap(True)
        self._subs_status.hide()
        right.addWidget(self._subs_status)

        self._rec_status = QLabel("")
        self._rec_status.setObjectName("hint")
        self._rec_status.setWordWrap(True)
        self._rec_status.hide()
        right.addWidget(self._rec_status)

        self._splitter.addWidget(self._right)
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setSizes([360, 840])

        QShortcut(QKeySequence("F11"), self).activated.connect(self._toggle_fullscreen)
        QShortcut(QKeySequence("Escape"), self).activated.connect(self._exit_fullscreen)

    # ---------------------------------------------------- motyw i stan
    def _on_theme_changed(self, *_args):
        key = self._theme.currentData() or DEFAULT_THEME
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(build_stylesheet(key))
        self._settings.setValue("theme", key)

    def _on_language_changed(self, *_args):
        code = self._language.currentData()
        if not code:
            return
        set_language(code)
        self._settings.setValue("language", code)
        if self._subtitle_enabled:
            self._subtitle_last_text = ""
            self._subtitle_request = 0
            self._player.clear_subtitle()
        self._retranslate_ui()

    def _retranslate_ui(self):
        self.setWindowTitle(tr("app_title"))
        if hasattr(self, "_title_bar"):
            self._title_bar.retranslate()
        self._language_label.setText(tr("language_label"))
        self._theme_label.setText(tr("theme_label"))
        self._search.setPlaceholderText(tr("search_placeholder"))
        self._only_favorites.setText(tr("only_favorites"))
        self._add_source_btn.setText(tr("add_custom_channel"))
        self._remove_source_btn.setText(tr("remove_custom_channel"))
        self._country.setToolTip(tr("country_filter"))
        self._category.setToolTip(tr("category_filter"))
        self._refresh.setText(tr("refresh_db"))
        self._play_btn.setText(tr("play"))
        self._pause_btn.setText(tr("pause"))
        self._stop_btn.setText(tr("stop"))
        self._volume_label.setText(tr("volume"))
        self._fullscreen_btn.setText(tr("fullscreen"))
        self._mute_btn.setToolTip(
            tr("unmute") if self._player.is_muted() else tr("mute")
        )
        self._update_subtitle_button()
        self._update_record_button()

        selected_theme = self._theme.currentData()
        self._theme.blockSignals(True)
        for index in range(self._theme.count()):
            self._theme.setItemText(index, theme_name(self._theme.itemData(index)))
        if selected_theme:
            self._theme.setCurrentIndex(self._theme.findData(selected_theme))
        self._theme.blockSignals(False)

        if self._current_channel_id:
            self._now.setText(
                tr("now_playing", name=self._current_channel_name)
            )
        else:
            self._now.setText(tr("no_channel"))
        self._refresh_epg_text()
        self._update_fav_button()
        self._player.retranslate()

        if self._catalog is not None or self._channels:
            self._build_search_index()
            self._populate_filters()
            self._apply_filters()
        elif self._load_failed:
            self._count.setText(tr("database_error"))
        elif self._loader is not None and self._loader.isRunning():
            self._count.setText(
                tr("downloading_db" if self._loading_force else "loading_db")
            )
        else:
            self._count.setText(tr("loading_db"))

    def _restore_state(self):
        volume = self._settings.value("volume", 70, type=int)
        self._volume.setValue(int(volume))
        self._player.set_volume(int(volume))

        theme = self._settings.value("theme", DEFAULT_THEME, type=str)
        if theme not in theme_names():
            theme = DEFAULT_THEME
        theme_index = self._theme.findData(theme)
        self._theme.blockSignals(True)
        self._theme.setCurrentIndex(theme_index if theme_index >= 0 else 0)
        self._theme.blockSignals(False)
        self._on_theme_changed()

        language = self._settings.value("language", "", type=str)
        if language not in LANGUAGE_CODES:
            language = current_language()
        language_index = self._language.findData(language)
        self._language.blockSignals(True)
        self._language.setCurrentIndex(language_index if language_index >= 0 else 0)
        self._language.blockSignals(False)
        set_language(self._language.currentData() or DEFAULT_LANGUAGE)

        raw_favorites = self._settings.value("favorites", [])
        if isinstance(raw_favorites, str):
            raw_favorites = [raw_favorites]
        self._favorites = {str(item) for item in (raw_favorites or [])}

    # ----------------------------------------------------- ładowanie
    def _start_loading(self, force: bool):
        if self._loader is not None and self._loader.isRunning():
            return
        self._refresh.setEnabled(False)
        self._load_failed = False
        self._loading_force = force
        self._count.setText(
            tr("downloading_db" if force else "loading_db")
        )
        self._loader = CatalogLoader(force=force, parent=self)
        self._loader.progress.connect(self._count.setText)
        self._loader.loaded.connect(self._on_loaded)
        self._loader.failed.connect(self._on_failed)
        self._loader.finished.connect(self._on_loader_finished)
        self._loader.start()

    def _on_loader_finished(self):
        self._refresh.setEnabled(True)

    def _on_loaded(self, catalog):
        self._catalog = catalog
        self._load_failed = False
        self._channels = catalog.playable_channels() + self._custom_channels
        self._build_search_index()
        self._logo_loader.reset()
        self._populate_filters()
        self._apply_filters()

    def _build_search_index(self):
        blob = {}
        for channel in self._channels:
            channel_id = channel.get("id")
            if not channel_id:
                continue
            parts = [
                channel.get("name"),
                *(channel.get("alt_names") or []),
                channel.get("network"),
                *(channel.get("owners") or []),
                channel.get("country"),
                channel.get("url"),
            ]
            country_code = channel.get("country") or ""
            country = (
                self._catalog.country_by_code.get(country_code)
                if self._catalog is not None
                else None
            )
            if country:
                parts.extend(
                    (country.get("name"), country.get("native_name"), country.get("code"))
                )
            parts.extend(COUNTRY_NAMES.get(country_code, {}).values())
            for category_id in channel.get("categories") or []:
                parts.append(category_id)
                category = (
                    self._catalog.category_by_id.get(category_id)
                    if self._catalog is not None
                    else None
                )
                if category:
                    parts.append(category.get("name"))
                parts.extend(CATEGORY_NAMES.get(category_id, {}).values())
            blob[channel_id] = _normalize(" ".join(str(p) for p in parts if p))
        self._search_blob = blob

    def _on_failed(self, message: str):
        self._load_failed = True
        self._channels = list(self._custom_channels)
        self._build_search_index()
        self._populate_filters()
        self._apply_filters()
        self._count.setText(tr("database_error"))
        QMessageBox.critical(
            self,
            tr("error_title"),
            tr("loading_db_failed", message=message),
        )

    def _populate_filters(self):
        selected_country = self._country.currentData()
        selected_category = self._category.currentData()
        self._country.blockSignals(True)
        self._category.blockSignals(True)
        try:
            self._country.clear()
            self._country.addItem(tr("all_countries"), None)
            country_entries = []
            for code in {c.get("country") for c in self._channels if c.get("country")}:
                country = (
                    self._catalog.country_by_code.get(code, {})
                    if self._catalog is not None
                    else {}
                )
                country_entries.append(
                    (
                        country_name(code, country.get("name", code)),
                        code,
                        self._country_flag(code, country.get("flag", "")),
                    )
                )
            for name, code, flag in sorted(
                country_entries, key=lambda entry: entry[0].casefold()
            ):
                self._country.addItem(f"{flag} {name}".strip(), code)

            self._category.clear()
            self._category.addItem(tr("all_categories"), None)
            category_entries = []
            for category_id in {
                category
                for channel in self._channels
                for category in (channel.get("categories") or [])
            }:
                category = (
                    self._catalog.category_by_id.get(category_id, {})
                    if self._catalog is not None
                    else {}
                )
                category_entries.append(
                    (
                        category_name(category_id, category.get("name", category_id)),
                        category_id,
                    )
                )
            for name, category_id in sorted(
                category_entries, key=lambda entry: entry[0].casefold()
            ):
                self._category.addItem(name, category_id)

            country_index = (
                self._country.findData(selected_country)
                if selected_country is not None
                else -1
            )
            self._country.setCurrentIndex(country_index if country_index >= 0 else 0)
            category_index = (
                self._category.findData(selected_category)
                if selected_category is not None
                else -1
            )
            self._category.setCurrentIndex(
                category_index if category_index >= 0 else 0
            )
        finally:
            self._country.blockSignals(False)
            self._category.blockSignals(False)

    # ----------------------------------------------------- ulubione
    def _save_favorites(self):
        self._settings.setValue("favorites", sorted(self._favorites))

    def _update_fav_button(self, *args):
        channel = self._selected_channel()
        if channel and channel.get("id") in self._favorites:
            self._fav_btn.setText(tr("remove_favorite"))
        else:
            self._fav_btn.setText(tr("add_favorite"))
        self._remove_source_btn.setEnabled(bool(channel and channel.get("custom")))

    def _toggle_favorite(self):
        channel = self._selected_channel()
        if not channel:
            QMessageBox.information(
                self, tr("info_title"), tr("select_channel_first")
            )
            return
        channel_id = channel.get("id")
        if channel_id in self._favorites:
            self._favorites.discard(channel_id)
        else:
            self._favorites.add(channel_id)
        self._save_favorites()
        self._apply_filters()
        self._update_fav_button()

    # ----------------------------------------------------- filtrowanie
    def _apply_filters(self):
        if self._catalog is None and not self._channels:
            return

        text = self._search.text().strip()
        tokens = _expand_query(text)
        country = self._country.currentData()
        category = self._category.currentData()
        only_favorites = self._only_favorites.isChecked()

        current = self._list.currentItem()
        selected_id = None
        if current is not None:
            data = current.data(Qt.UserRole)
            selected_id = data.get("id") if data else None

        results = []
        for channel in self._channels:
            channel_id = channel.get("id")
            if only_favorites and channel_id not in self._favorites:
                continue
            if country and channel.get("country") != country:
                continue
            if category and category not in (channel.get("categories") or []):
                continue
            if tokens:
                blob = self._search_blob.get(channel_id, "")
                if not blob or any(not _token_matches(token, blob) for token in tokens):
                    continue
            results.append(channel)

        total = len(results)
        self._list.clear()
        self._item_by_channel = {}
        selected_item = None

        for channel in results[:MAX_RESULTS]:
            channel_id = channel.get("id")
            country_code = channel.get("country")
            flag = (
                self._catalog.country_flag(country_code)
                if self._catalog is not None
                else self._country_flag(country_code)
            )
            categories = ", ".join(
                category_name(
                    category_id,
                    (
                        (self._catalog.category_by_id.get(category_id) or {}).get(
                            "name", category_id
                        )
                        if self._catalog is not None
                        else category_id
                    ),
                )
                for category_id in (channel.get("categories") or [])
            )
            star = "★ " if channel_id in self._favorites else ""
            label = f"{star}{flag} {channel.get('name', '')}".strip()
            if categories:
                label += f"   ·   {categories}"
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, channel)
            self._list.addItem(item)
            self._item_by_channel[channel_id] = item
            if channel_id == selected_id:
                selected_item = item

        if selected_item is not None:
            self._list.setCurrentItem(selected_item)

        for channel in results[:MAX_LOGO_ITEMS]:
            if self._catalog is None or channel.get("custom"):
                continue
            channel_id = channel.get("id")
            self._logo_loader.request(channel_id, self._catalog.logo_url(channel_id))

        if total > MAX_RESULTS:
            self._count.setText(
                tr("count_limited", shown=MAX_RESULTS, total=total)
            )
        else:
            self._count.setText(tr("count_channels", total=total))

    def _load_custom_channels(self) -> list[dict]:
        saved = self._settings.value("custom_channels", [])
        if isinstance(saved, dict):
            saved = [saved]
        entries = saved if isinstance(saved, (list, tuple)) else []
        channels = []
        seen_ids = set()
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            name = str(entry.get("name") or "").strip()
            url = str(entry.get("url") or "").strip()
            if name and self._valid_source_url(url):
                source_id = str(entry.get("id") or "")
                if not source_id.startswith("custom:") or source_id in seen_ids:
                    source_id = f"custom:{uuid4().hex}"
                seen_ids.add(source_id)
                channels.append(
                    {
                        "id": source_id,
                        "name": name,
                        "url": url,
                        "custom": True,
                        "categories": [],
                    }
                )
        return channels

    @staticmethod
    def _valid_source_url(url: str) -> bool:
        try:
            parsed = urlsplit(url.strip())
            return (
                parsed.scheme.lower() in {"http", "https"}
                and bool(parsed.hostname)
                and parsed.username is None
                and parsed.password is None
            )
        except ValueError:
            return False

    @staticmethod
    def _country_flag(code: str | None, fallback: str = "") -> str:
        if fallback:
            return fallback
        code = code or ""
        if len(code) == 2 and code.isascii() and code.isalpha():
            return "".join(chr(ord(char.upper()) + 127397) for char in code)
        return ""

    def _save_custom_channels(self):
        self._settings.setValue(
            "custom_channels",
            [
                {"id": channel["id"], "name": channel["name"], "url": channel["url"]}
                for channel in self._custom_channels
            ],
        )

    def _refresh_channels(self):
        if self._catalog is not None:
            self._channels = self._catalog.playable_channels() + self._custom_channels
        else:
            self._channels = list(self._custom_channels)
        self._build_search_index()
        self._populate_filters()
        self._apply_filters()

    def _add_custom_channel(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("add_custom_channel"))
        form = QFormLayout(dialog)
        name_input = QLineEdit(dialog)
        name_input.setPlaceholderText(tr("custom_channel_name_hint"))
        url_input = QLineEdit(dialog)
        url_input.setPlaceholderText("https://…")
        form.addRow(tr("custom_channel_name"), name_input)
        form.addRow(tr("custom_channel_url"), url_input)
        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel, parent=dialog
        )
        form.addRow(buttons)
        buttons.rejected.connect(dialog.reject)

        def save_channel():
            name = name_input.text().strip()
            url = url_input.text().strip()
            if not name or not self._valid_source_url(url):
                QMessageBox.warning(self, tr("error_title"), tr("custom_url_invalid"))
                return
            host = (urlsplit(url).hostname or "").lower()
            platform = next(
                (
                    domain
                    for domain in ("youtube", "twitch", "rumble", "kick")
                    if domain in host
                ),
                "",
            )
            self._custom_channels.append(
                {
                    "id": f"custom:{uuid4().hex}",
                    "name": name,
                    "url": url,
                    "custom": True,
                    "network": platform,
                    "categories": [],
                }
            )
            self._save_custom_channels()
            self._refresh_channels()
            dialog.accept()

        buttons.accepted.connect(save_channel)
        dialog.resize(500, 140)
        dialog.exec()

    def _remove_custom_channel(self):
        channel = self._selected_channel()
        if not channel or not channel.get("custom"):
            return
        channel_id = channel.get("id")
        self._custom_channels = [
            item for item in self._custom_channels if item.get("id") != channel_id
        ]
        self._favorites.discard(channel_id)
        self._save_custom_channels()
        self._save_favorites()
        self._refresh_channels()

    def _on_logo_ready(self, channel_id: str, icon):
        item = self._item_by_channel.get(channel_id)
        if item is not None:
            item.setIcon(icon)

    # ----------------------------------------------------- odtwarzanie
    def _selected_channel(self):
        item = self._list.currentItem()
        return item.data(Qt.UserRole) if item else None

    def _on_item_activated(self, item: QListWidgetItem):
        channel = item.data(Qt.UserRole)
        if channel:
            self._play_channel(channel)

    def _play_selected(self):
        channel = self._selected_channel()
        if channel is None:
            QMessageBox.information(
                self, tr("info_title"), tr("select_channel_first")
            )
            return
        self._play_channel(channel)

    def _play_channel(self, channel):
        if not self._catalog and not channel.get("custom"):
            return
        self._stop_recording()
        self._reset_subtitles()
        self._stream_request_id += 1
        request_id = self._stream_request_id
        for resolver in self._stream_resolvers:
            if resolver.isRunning():
                resolver.requestInterruption()

        if channel.get("custom"):
            stream = {"url": channel["url"]}
        else:
            stream = self._catalog.best_stream(channel.get("id", ""))
        if not stream:
            QMessageBox.warning(
                self, tr("no_stream_title"), tr("no_stream_text")
            )
            return
        self._current_channel_id = channel.get("id")
        self._current_channel_name = channel.get("name", "")
        self._current_stream = None
        self._player.stop()

        if requires_resolution(stream["url"]):
            self._now.setText(tr("now_playing", name=self._current_channel_name))
            self._epg.setText(tr("resolving_stream"))
            resolver = StreamResolver(request_id, stream["url"], self)
            self._stream_resolvers.append(resolver)
            resolver.resolved.connect(self._on_stream_resolved)
            resolver.failed.connect(self._on_stream_resolution_failed)
            resolver.finished.connect(
                lambda worker=resolver: self._on_stream_resolver_finished(worker)
            )
            resolver.start()
            return

        self._start_playback(channel, stream, request_id)

    def _on_stream_resolved(self, request_id: int, stream: dict):
        if request_id != self._stream_request_id:
            return
        channel = next(
            (
                item
                for item in self._channels
                if item.get("id") == self._current_channel_id
            ),
            None,
        )
        if channel is None:
            return
        self._start_playback(channel, stream, request_id)

    def _on_stream_resolution_failed(self, request_id: int, message: str):
        if request_id != self._stream_request_id:
            return
        self._player.stop()
        self._reset_subtitles()
        self._current_stream = None
        self._current_channel_id = None
        self._current_channel_name = ""
        self._epg_loading = False
        self._epg_programmes = None
        self._now.setText(tr("no_channel"))
        self._refresh_epg_text()
        QMessageBox.warning(
            self,
            tr("play_error_title"),
            tr("stream_resolution_failed", error=message),
        )

    def _on_stream_resolver_finished(self, resolver: StreamResolver):
        if resolver in self._stream_resolvers:
            self._stream_resolvers.remove(resolver)
        resolver.deleteLater()

    def _finish_close_after_resolving(self):
        if not any(resolver.isRunning() for resolver in self._stream_resolvers):
            self._close_pending = False
            self.close()

    def _start_playback(self, channel, stream: dict, request_id: int):
        if request_id != self._stream_request_id:
            return
        self._current_stream = stream
        try:
            self._player.play(
                stream["url"],
                stream.get("referrer"),
                stream.get("user_agent"),
                stream.get("headers"),
                stream.get("audio_url"),
            )
        except Exception as exc:  # noqa: BLE001
            self._current_stream = None
            QMessageBox.critical(self, tr("play_error_title"), str(exc))
            return
        self._current_channel_name = channel.get("name", "")
        self._now.setText(tr("now_playing", name=self._current_channel_name))
        if channel.get("custom"):
            self._epg_loading = False
            self._epg_programmes = None
            self._refresh_epg_text()
        else:
            self._start_epg(channel)

    def _stop(self):
        self._stream_request_id += 1
        self._cancel_epg()
        self._stop_recording()
        self._player.stop()
        self._current_stream = None
        self._reset_subtitles()
        self._now.setText(tr("no_channel"))
        self._current_channel_id = None
        self._current_channel_name = ""
        self._epg_loading = False
        self._epg_programmes = None
        self._refresh_epg_text()

    def _on_volume(self, value: int):
        self._player.set_volume(value)
        self._settings.setValue("volume", value)

    def _toggle_mute(self):
        muted = self._player.toggle_mute()
        self._mute_btn.setText("🔇" if muted else "🔊")
        self._mute_btn.setToolTip(tr("unmute") if muted else tr("mute"))

    # ----------------------------------------------------- napisy
    def _update_subtitle_button(self):
        active = self._subtitle_enabled
        self._subs_btn.blockSignals(True)
        self._subs_btn.setChecked(active)
        self._subs_btn.setText(
            tr("subtitles_on", lang=current_language().upper())
            if active
            else tr("subtitles_off")
        )
        self._subs_btn.setToolTip(
            tr("subtitles_on", lang=current_language().upper())
            if active
            else tr("subtitles_off")
        )
        self._subs_btn.blockSignals(False)

    def _set_subtitle_status(self, text: str):
        if text:
            self._subs_status.setText(text)
            self._subs_status.show()
        else:
            self._subs_status.clear()
            self._subs_status.hide()

    def _toggle_subtitles(self):
        if self._subtitle_enabled:
            self._disable_subtitles(restore=True)
            return
        if not self._current_channel_id or not self._current_stream:
            QMessageBox.information(
                self, tr("info_title"), tr("subtitles_select_first")
            )
            self._update_subtitle_button()
            return
        self._subtitle_enabled = True
        self._subtitle_wait_started = time.monotonic()
        self._subtitle_last_text = ""
        self._subtitle_request = 0
        self._player.prepare_subtitles()
        self._subtitle_timer.start()
        self._set_subtitle_status(tr("subtitles_waiting"))
        self._update_subtitle_button()

    def _disable_subtitles(self, restore: bool):
        self._subtitle_enabled = False
        self._subtitle_timer.stop()
        self._subtitle_last_text = ""
        self._player.clear_subtitle()
        if restore:
            self._player.restore_subtitles()
        self._set_subtitle_status("")
        self._update_subtitle_button()

    def _reset_subtitles(self):
        self._subtitle_enabled = False
        self._subtitle_timer.stop()
        self._subtitle_last_text = ""
        self._subtitle_request = 0
        self._player.restore_subtitles()
        self._set_subtitle_status("")
        self._update_subtitle_button()

    def _poll_subtitles(self):
        if not self._subtitle_enabled or not self._current_channel_id:
            return
        if not self._player.prepare_subtitles():
            if (
                self._subtitle_wait_started
                and time.monotonic() - self._subtitle_wait_started > 12
            ):
                self._set_subtitle_status(tr("subtitles_none"))
            return
        self._set_subtitle_status("")
        text = self._player.current_subtitle_text()
        if text == self._subtitle_last_text:
            return
        self._subtitle_last_text = text
        if not text:
            self._player.clear_subtitle()
            return
        self._subtitle_request = self._subtitle_translator.translate(
            text, current_language()
        )

    def _on_subtitle_translated(self, sequence: int, text: str):
        if not self._subtitle_enabled or sequence != self._subtitle_request:
            return
        self._set_subtitle_status("")
        self._player.show_subtitle(text)

    def _on_subtitle_failed(self, sequence: int):
        if not self._subtitle_enabled or sequence != self._subtitle_request:
            return
        self._player.clear_subtitle()
        self._set_subtitle_status(tr("subtitles_error"))

    # --------------------------------------------------- nagrywanie
    def _update_record_button(self):
        recording = self._recorder.is_recording
        if recording:
            elapsed = max(0, int(time.monotonic() - self._recording_started_at))
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)
            duration = (
                f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                if hours
                else f"{minutes:02d}:{seconds:02d}"
            )
            self._record_btn.setText(f"⏺ {duration}")
            self._record_btn.setToolTip(tr("stop_recording"))
        else:
            self._record_btn.setText(tr("record"))
            self._record_btn.setToolTip(tr("record"))
        self._record_btn.setProperty("recording", "true" if recording else "false")
        self._record_btn.style().unpolish(self._record_btn)
        self._record_btn.style().polish(self._record_btn)

    def _toggle_recording(self):
        if self._recorder.is_recording:
            self._recorder.stop()
            return
        if not self._current_channel_id or not self._current_stream:
            QMessageBox.information(
                self, tr("info_title"), tr("recording_requires_playback")
            )
            return
        stream = self._current_stream
        self._recording_path = ""
        self._recorder.start(
            stream["url"],
            self._current_channel_name,
            stream.get("referrer"),
            stream.get("user_agent"),
            stream.get("headers"),
            stream.get("audio_url"),
        )

    def _on_recording_started(self, path: str):
        self._recording_path = path
        self._recording_started_at = time.monotonic()
        self._record_timer.start()
        self._update_record_button()
        self._record_btn.setToolTip(path)
        self._rec_status.setText(tr("recording", name=os.path.basename(path)))
        self._rec_status.show()

    def _on_recording_fallback(self, path: str):
        self._recording_path = path
        self._record_btn.setToolTip(path)
        self._rec_status.setText(
            tr("recording_fallback", name=os.path.basename(path))
        )
        self._rec_status.show()

    def _on_recording_stopped(self, path: str):
        self._recording_path = ""
        self._record_timer.stop()
        self._update_record_button()
        self._record_btn.setToolTip("")
        if self._closing:
            return
        self._rec_status.setText(tr("recording_saved", name=os.path.basename(path)))
        self._rec_status.show()

    def _on_recording_failed(self, message: str):
        self._recording_path = ""
        self._record_timer.stop()
        self._update_record_button()
        self._record_btn.setToolTip("")
        self._rec_status.hide()
        if self._closing:
            return
        QMessageBox.warning(self, tr("record"), message)

    def _stop_recording(self):
        if self._recorder.is_recording:
            self._recorder.stop()

    # ----------------------------------------------------- EPG
    def _refresh_epg_text(self):
        if not self._current_channel_id:
            self._epg.setText(tr("epg_prefix"))
        elif self._epg_loading:
            self._epg.setText(tr("epg_loading"))
        elif self._epg_programmes is not None:
            self._epg.setText(
                tr("epg_header") + "\n" + self._format_programmes(self._epg_programmes)
            )
        else:
            self._epg.setText(tr("epg_none"))

    def _cancel_epg(self):
        worker = self._epg_worker
        if worker is not None and worker.isRunning():
            worker.requestInterruption()

    def _on_epg_finished(self, worker):
        if self._epg_worker is worker:
            self._epg_worker = None
        worker.deleteLater()

    def _start_epg(self, channel):
        self._cancel_epg()
        self._current_channel_id = channel.get("id")
        self._current_channel_name = channel.get("name", "")
        self._epg_loading = True
        self._epg_programmes = None
        self._refresh_epg_text()
        sources = sources_for_channel(
            channel.get("id", ""), channel.get("country")
        )
        if not sources:
            self._epg_loading = False
            self._refresh_epg_text()
            return

        worker = EpgWorker(
            channel["id"], channel.get("name", ""), sources, parent=self
        )
        worker.ready.connect(self._on_epg_ready)
        worker.failed.connect(self._on_epg_failed)
        worker.finished.connect(lambda w=worker: self._on_epg_finished(w))
        self._epg_worker = worker
        worker.start()

    def _on_epg_ready(self, channel_id: str, programmes: list):
        if channel_id != self._current_channel_id:
            return
        self._epg_loading = False
        self._epg_programmes = programmes
        self._refresh_epg_text()

    def _on_epg_failed(self, channel_id: str, _message: str):
        if channel_id != self._current_channel_id:
            return
        self._epg_loading = False
        self._epg_programmes = None
        self._refresh_epg_text()

    def _format_programmes(self, programmes: list) -> str:
        now = time.time()
        lines = []
        for programme in programmes:
            start = datetime.fromtimestamp(programme["start_ts"]).strftime("%H:%M")
            stop_ts = programme.get("stop_ts")
            stop = datetime.fromtimestamp(stop_ts).strftime("%H:%M") if stop_ts else "?"
            is_live = programme["start_ts"] <= now and (stop_ts is None or now < stop_ts)
            tag = tr("epg_now") if is_live else tr("epg_next")
            lines.append(f"{tag}  {start}–{stop}  {programme['title']}")
        return "\n".join(lines)

    # ----------------------------------------------------- pełny ekran
    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self._exit_fullscreen()
        else:
            self._left.hide()
            self.showFullScreen()

    def _exit_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        self._left.show()

    # ----------------------------------------------------- okno
    def resizeEvent(self, event):
        super().resizeEvent(event)
        grip = getattr(self, "_size_grip", None)
        if grip is not None:
            grip.move(
                self.width() - grip.width() - 2,
                self.height() - grip.height() - 2,
            )
            grip.raise_()

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if hasattr(self, "_title_bar"):
                self._title_bar.update_state()
                self._title_bar.setVisible(not self.isFullScreen())
            if hasattr(self, "_size_grip"):
                self._size_grip.setVisible(not self.isFullScreen())
        super().changeEvent(event)

    # ----------------------------------------------------- zamknięcie
    def closeEvent(self, event):
        running_resolvers = [
            resolver for resolver in self._stream_resolvers if resolver.isRunning()
        ]
        if running_resolvers:
            for resolver in running_resolvers:
                resolver.requestInterruption()
            self.setEnabled(False)
            if not self._close_pending:
                self._close_pending = True
                for resolver in running_resolvers:
                    resolver.finished.connect(self._finish_close_after_resolving)
            event.ignore()
            return

        self._closing = True
        self._subtitle_timer.stop()
        self._record_timer.stop()
        self._recorder.shutdown()
        if self._loader is not None and self._loader.isRunning():
            self._loader.requestInterruption()
            self._loader.wait(5000)
        epg = self._epg_worker
        if epg is not None and epg.isRunning():
            epg.requestInterruption()
            if not epg.wait(2000):
                self.setEnabled(False)
                if not self._close_pending:
                    self._close_pending = True
                    epg.finished.connect(self._finish_close_after_epg)
                event.ignore()
                return
        self._logo_loader.shutdown()
        self._player.shutdown()
        super().closeEvent(event)

    def _finish_close_after_epg(self):
        self._close_pending = False
        self.close()

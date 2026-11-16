"""Tłumaczenia interfejsu OmniTV.

Kraj pochodzi z wygenerowanego modułu ``countries_i18n``, kategorie i motywy
są zdefiniowane poniżej. Wybór języka jest globalny (``set_language``) i
używany przez cały interfejs.
"""

from __future__ import annotations

from omnity.countries_i18n import COUNTRY_NAMES

DEFAULT_LANGUAGE = "pl"

LANGUAGES = (
    ("pl", "Polski"),
    ("en", "English"),
    ("de", "Deutsch"),
    ("ru", "Русский"),
    ("fr", "Français"),
    ("it", "Italiano"),
    ("es", "Español"),
)

LANGUAGE_CODES = {code for code, _name in LANGUAGES}

_current_language = DEFAULT_LANGUAGE


def current_language() -> str:
    return _current_language


def set_language(code: str) -> str:
    global _current_language
    if code in LANGUAGE_CODES:
        _current_language = code
    return _current_language


def _fallback_language() -> str:
    return "en"


def tr(key: str, **kwargs) -> str:
    text = (
        TRANSLATIONS.get(_current_language, {}).get(key)
        or TRANSLATIONS[_fallback_language()].get(key)
        or key
    )
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    return text


CATEGORY_NAMES = {
    "auto": {
        "pl": "Auto", "en": "Auto", "de": "Auto", "ru": "Авто",
        "fr": "Auto", "it": "Auto", "es": "Auto",
    },
    "animation": {
        "pl": "Animacja", "en": "Animation", "de": "Animation",
        "ru": "Анимация", "fr": "Animation", "it": "Animazione",
        "es": "Animación",
    },
    "business": {
        "pl": "Biznes", "en": "Business", "de": "Wirtschaft",
        "ru": "Бизнес", "fr": "Affaires", "it": "Affari", "es": "Negocios",
    },
    "classic": {
        "pl": "Klasyka", "en": "Classic", "de": "Klassiker",
        "ru": "Классика", "fr": "Classique", "it": "Classico", "es": "Clásico",
    },
    "comedy": {
        "pl": "Komedia", "en": "Comedy", "de": "Komödie",
        "ru": "Комедия", "fr": "Comédie", "it": "Commedia", "es": "Comedia",
    },
    "cooking": {
        "pl": "Gotowanie", "en": "Cooking", "de": "Kochen",
        "ru": "Кулинария", "fr": "Cuisine", "it": "Cucina", "es": "Cocina",
    },
    "culture": {
        "pl": "Kultura", "en": "Culture", "de": "Kultur",
        "ru": "Культура", "fr": "Culture", "it": "Cultura", "es": "Cultura",
    },
    "documentary": {
        "pl": "Dokument", "en": "Documentary", "de": "Dokumentation",
        "ru": "Документальное", "fr": "Documentaire", "it": "Documentario",
        "es": "Documental",
    },
    "education": {
        "pl": "Edukacja", "en": "Education", "de": "Bildung",
        "ru": "Образование", "fr": "Éducation", "it": "Istruzione",
        "es": "Educación",
    },
    "entertainment": {
        "pl": "Rozrywka", "en": "Entertainment", "de": "Unterhaltung",
        "ru": "Развлечения", "fr": "Divertissement", "it": "Intrattenimento",
        "es": "Entretenimiento",
    },
    "family": {
        "pl": "Rodzina", "en": "Family", "de": "Familie",
        "ru": "Семья", "fr": "Famille", "it": "Famiglia", "es": "Familia",
    },
    "general": {
        "pl": "Ogólne", "en": "General", "de": "Allgemein",
        "ru": "Общее", "fr": "Général", "it": "Generale", "es": "General",
    },
    "interactive": {
        "pl": "Interaktywne", "en": "Interactive", "de": "Interaktiv",
        "ru": "Интерактивное", "fr": "Interactif", "it": "Interattivo",
        "es": "Interactivo",
    },
    "kids": {
        "pl": "Dzieci", "en": "Kids", "de": "Kinder",
        "ru": "Дети", "fr": "Enfants", "it": "Bambini", "es": "Niños",
    },
    "legislative": {
        "pl": "Legislacja", "en": "Legislative", "de": "Gesetzgebung",
        "ru": "Законодательство", "fr": "Législatif", "it": "Legislativo",
        "es": "Legislativo",
    },
    "lifestyle": {
        "pl": "Styl życia", "en": "Lifestyle", "de": "Lifestyle",
        "ru": "Образ жизни", "fr": "Mode de vie", "it": "Stile di vita",
        "es": "Estilo de vida",
    },
    "movies": {
        "pl": "Filmy", "en": "Movies", "de": "Filme",
        "ru": "Фильмы", "fr": "Films", "it": "Film", "es": "Películas",
    },
    "music": {
        "pl": "Muzyka", "en": "Music", "de": "Musik",
        "ru": "Музыка", "fr": "Musique", "it": "Musica", "es": "Música",
    },
    "news": {
        "pl": "Wiadomości", "en": "News", "de": "Nachrichten",
        "ru": "Новости", "fr": "Actualités", "it": "Notizie", "es": "Noticias",
    },
    "outdoor": {
        "pl": "Outdoor", "en": "Outdoor", "de": "Outdoor",
        "ru": "Природа", "fr": "Plein air", "it": "All'aperto",
        "es": "Aire libre",
    },
    "public": {
        "pl": "Publiczne", "en": "Public", "de": "Öffentlich",
        "ru": "Общественное", "fr": "Public", "it": "Pubblico",
        "es": "Público",
    },
    "relax": {
        "pl": "Relaks", "en": "Relax", "de": "Entspannung",
        "ru": "Релакс", "fr": "Détente", "it": "Relax", "es": "Relajación",
    },
    "religious": {
        "pl": "Religijne", "en": "Religious", "de": "Religion",
        "ru": "Религия", "fr": "Religion", "it": "Religione", "es": "Religión",
    },
    "series": {
        "pl": "Seriale", "en": "Series", "de": "Serien",
        "ru": "Сериалы", "fr": "Séries", "it": "Serie", "es": "Series",
    },
    "science": {
        "pl": "Nauka", "en": "Science", "de": "Wissenschaft",
        "ru": "Наука", "fr": "Science", "it": "Scienza", "es": "Ciencia",
    },
    "shop": {
        "pl": "Zakupy", "en": "Shopping", "de": "Einkaufen",
        "ru": "Покупки", "fr": "Achats", "it": "Acquisti", "es": "Compras",
    },
    "sports": {
        "pl": "Sport", "en": "Sports", "de": "Sport",
        "ru": "Спорт", "fr": "Sport", "it": "Sport", "es": "Deportes",
    },
    "travel": {
        "pl": "Podróże", "en": "Travel", "de": "Reisen",
        "ru": "Путешествия", "fr": "Voyages", "it": "Viaggi", "es": "Viajes",
    },
    "weather": {
        "pl": "Pogoda", "en": "Weather", "de": "Wetter",
        "ru": "Погода", "fr": "Météo", "it": "Meteo", "es": "Clima",
    },
    "xxx": {
        "pl": "XXX", "en": "XXX", "de": "XXX", "ru": "XXX",
        "fr": "XXX", "it": "XXX", "es": "XXX",
    },
}

THEME_NAMES = {
    "Ciemny": {
        "pl": "Ciemny", "en": "Dark", "de": "Dunkel", "ru": "Тёмная",
        "fr": "Sombre", "it": "Scuro", "es": "Oscuro",
    },
    "Jasny": {
        "pl": "Jasny", "en": "Light", "de": "Hell", "ru": "Светлая",
        "fr": "Clair", "it": "Chiaro", "es": "Claro",
    },
    "Nocny błękit": {
        "pl": "Nocny błękit", "en": "Midnight Blue", "de": "Mitternachtsblau",
        "ru": "Полуночный синий", "fr": "Bleu nuit", "it": "Blu notte",
        "es": "Azul medianoche",
    },
    "Leśny": {
        "pl": "Leśny", "en": "Forest", "de": "Wald", "ru": "Лесная",
        "fr": "Forêt", "it": "Foresta", "es": "Bosque",
    },
    "Kontrast": {
        "pl": "Kontrast", "en": "Contrast", "de": "Kontrast",
        "ru": "Контраст", "fr": "Contraste", "it": "Contrasto",
        "es": "Contraste",
    },
    "Fiolet": {
        "pl": "Fiolet", "en": "Violet", "de": "Violett", "ru": "Фиолетовый",
        "fr": "Violet", "it": "Viola", "es": "Violeta",
    },
}


def country_name(code: str, fallback: str | None = None, lang: str | None = None) -> str:
    language = lang or _current_language
    names = COUNTRY_NAMES.get(code or "", {})
    return names.get(language) or names.get("en") or fallback or code or ""


def category_name(category_id: str, fallback: str | None = None, lang: str | None = None) -> str:
    language = lang or _current_language
    names = CATEGORY_NAMES.get(category_id or "", {})
    return names.get(language) or names.get("en") or fallback or category_id or ""


def theme_name(theme_key: str, lang: str | None = None) -> str:
    language = lang or _current_language
    names = THEME_NAMES.get(theme_key, {})
    return names.get(language) or theme_key


TRANSLATIONS = {
    "pl": {
        "app_title": "OmniTV — darmowe kanały online",
        "language_label": "Język:",
        "theme_label": "Motyw:",
        "search_placeholder": "Szukaj kanału, kategorii lub kraju...",
        "add_favorite": "☆ Dodaj do ulubionych",
        "remove_favorite": "★ Usuń z ulubionych",
        "only_favorites": "Tylko ulubione",
        "loading_db": "Ładowanie bazy kanałów...",
        "downloading_db": "Pobieranie bazy kanałów...",
        "refresh_db": "Odśwież bazę kanałów",
        "no_channel": "Nie odtwarzasz żadnego kanału.",
        "now_playing": "Odtwarzanie: {name}",
        "epg_prefix": "Program TV: —",
        "play": "▶ Odtwórz",
        "pause": "⏸ Pauza",
        "stop": "⏹ Stop",
        "volume": "Głośność",
        "mute": "Wycisz",
        "unmute": "Włącz dźwięk",
        "fullscreen": "⛶ Pełny ekran",
        "all_countries": "Wszystkie kraje",
        "all_categories": "Wszystkie kategorie",
        "error_title": "Błąd",
        "info_title": "Informacja",
        "loading_db_failed": "Nie udało się załadować bazy kanałów:\n\n{message}",
        "database_error": "Błąd ładowania bazy.",
        "select_channel_first": "Najpierw wybierz kanał z listy.",
        "no_stream_title": "Brak strumienia",
        "no_stream_text": "Ten kanał nie ma dostępnego strumienia.",
        "play_error_title": "Błąd odtwarzania",
        "epg_loading": "Program TV: pobieranie...",
        "epg_none": "Program TV: brak danych EPG dla tego kanału.",
        "epg_header": "Program TV:",
        "epg_now": "TERAZ",
        "epg_next": "POTEM",
        "count_channels": "Kanałów: {total}",
        "count_limited": "Pokazano {shown} z {total} kanałów — zawęź filtry.",
        "player_unavailable": (
            "Odtwarzacz libmpv jest niedostępny.\n\n"
            "Ubuntu/Debian:  sudo apt install libmpv2\n"
            "Windows: umieść libmpv-2.dll obok aplikacji.\n\n"
            "Szczegóły: {error}"
        ),
        "player_hint": "Kliknij dwukrotnie kanał na liście, aby rozpocząć odtwarzanie.",
        "mpv_unavailable": "libmpv / python-mpv nie jest dostępny. {error}",
        "mpv_locale_error": (
            "Nie można zainicjować libmpv (LC_NUMERIC nie jest ustawione "
            "na 'C'). Spróbuj uruchomić: LC_ALL=C omnity"
        ),
        "progress_downloading": "Pobieranie {name}...",
        "progress_done": "Gotowe.",
        "download_cancelled": "przerwano pobieranie",
        "download_stopped": "przerwano",
        "download_failed": "Nie udało się pobrać {name}: {error}",
    },
    "en": {
        "app_title": "OmniTV — free online TV",
        "language_label": "Language:",
        "theme_label": "Theme:",
        "search_placeholder": "Search channel, category or country...",
        "add_favorite": "☆ Add to favorites",
        "remove_favorite": "★ Remove from favorites",
        "only_favorites": "Favorites only",
        "loading_db": "Loading channel database...",
        "downloading_db": "Downloading channel database...",
        "refresh_db": "Refresh channel database",
        "no_channel": "No channel is playing.",
        "now_playing": "Playing: {name}",
        "epg_prefix": "TV guide: —",
        "play": "▶ Play",
        "pause": "⏸ Pause",
        "stop": "⏹ Stop",
        "volume": "Volume",
        "mute": "Mute",
        "unmute": "Unmute",
        "fullscreen": "⛶ Full screen",
        "all_countries": "All countries",
        "all_categories": "All categories",
        "error_title": "Error",
        "info_title": "Information",
        "loading_db_failed": "Failed to load the channel database:\n\n{message}",
        "database_error": "Failed to load the database.",
        "select_channel_first": "Select a channel from the list first.",
        "no_stream_title": "No stream",
        "no_stream_text": "This channel has no available stream.",
        "play_error_title": "Playback error",
        "epg_loading": "TV guide: loading...",
        "epg_none": "TV guide: no EPG data for this channel.",
        "epg_header": "TV guide:",
        "epg_now": "NOW",
        "epg_next": "NEXT",
        "count_channels": "Channels: {total}",
        "count_limited": "Showing {shown} of {total} channels — narrow your filters.",
        "player_unavailable": (
            "The libmpv player is unavailable.\n\n"
            "Ubuntu/Debian:  sudo apt install libmpv2\n"
            "Windows: place libmpv-2.dll next to the application.\n\n"
            "Details: {error}"
        ),
        "player_hint": "Double-click a channel in the list to start playback.",
        "mpv_unavailable": "libmpv / python-mpv is unavailable. {error}",
        "mpv_locale_error": (
            "Could not initialize libmpv (LC_NUMERIC is not set to 'C'). "
            "Try running: LC_ALL=C omnity"
        ),
        "progress_downloading": "Downloading {name}...",
        "progress_done": "Done.",
        "download_cancelled": "download cancelled",
        "download_stopped": "cancelled",
        "download_failed": "Failed to download {name}: {error}",
    },
    "de": {
        "app_title": "OmniTV — kostenloses Online-TV",
        "language_label": "Sprache:",
        "theme_label": "Design:",
        "search_placeholder": "Sender, Kategorie oder Land suchen...",
        "add_favorite": "☆ Zu Favoriten hinzufügen",
        "remove_favorite": "★ Aus Favoriten entfernen",
        "only_favorites": "Nur Favoriten",
        "loading_db": "Senderdatenbank wird geladen...",
        "downloading_db": "Senderdatenbank wird heruntergeladen...",
        "refresh_db": "Senderdatenbank aktualisieren",
        "no_channel": "Kein Sender wird abgespielt.",
        "now_playing": "Wiedergabe: {name}",
        "epg_prefix": "TV-Programm: —",
        "play": "▶ Abspielen",
        "pause": "⏸ Pause",
        "stop": "⏹ Stopp",
        "volume": "Lautstärke",
        "mute": "Stummschalten",
        "unmute": "Ton einschalten",
        "fullscreen": "⛶ Vollbild",
        "all_countries": "Alle Länder",
        "all_categories": "Alle Kategorien",
        "error_title": "Fehler",
        "info_title": "Information",
        "loading_db_failed": "Senderdatenbank konnte nicht geladen werden:\n\n{message}",
        "database_error": "Fehler beim Laden der Datenbank.",
        "select_channel_first": "Wähle zuerst einen Sender aus der Liste.",
        "no_stream_title": "Kein Stream",
        "no_stream_text": "Für diesen Sender ist kein Stream verfügbar.",
        "play_error_title": "Wiedergabefehler",
        "epg_loading": "TV-Programm: wird geladen...",
        "epg_none": "TV-Programm: keine EPG-Daten für diesen Sender.",
        "epg_header": "TV-Programm:",
        "epg_now": "JETZT",
        "epg_next": "DANACH",
        "count_channels": "Sender: {total}",
        "count_limited": "{shown} von {total} Sendern angezeigt — Filter einschränken.",
        "player_unavailable": (
            "Der libmpv-Player ist nicht verfügbar.\n\n"
            "Ubuntu/Debian:  sudo apt install libmpv2\n"
            "Windows: libmpv-2.dll neben die Anwendung legen.\n\n"
            "Details: {error}"
        ),
        "player_hint": "Doppelklicke einen Sender in der Liste, um die Wiedergabe zu starten.",
        "mpv_unavailable": "libmpv / python-mpv ist nicht verfügbar. {error}",
        "mpv_locale_error": (
            "libmpv konnte nicht initialisiert werden (LC_NUMERIC ist nicht "
            "auf 'C' gesetzt). Starte mit: LC_ALL=C omnity"
        ),
        "progress_downloading": "Lade {name} herunter...",
        "progress_done": "Fertig.",
        "download_cancelled": "Download abgebrochen",
        "download_stopped": "abgebrochen",
        "download_failed": "Download von {name} fehlgeschlagen: {error}",
    },
    "ru": {
        "app_title": "OmniTV — бесплатное онлайн-ТВ",
        "language_label": "Язык:",
        "theme_label": "Тема:",
        "search_placeholder": "Поиск канала, категории или страны...",
        "add_favorite": "☆ В избранное",
        "remove_favorite": "★ Убрать из избранного",
        "only_favorites": "Только избранные",
        "loading_db": "Загрузка базы каналов...",
        "downloading_db": "Скачивание базы каналов...",
        "refresh_db": "Обновить базу каналов",
        "no_channel": "Канал не воспроизводится.",
        "now_playing": "Воспроизведение: {name}",
        "epg_prefix": "Телепрограмма: —",
        "play": "▶ Воспроизвести",
        "pause": "⏸ Пауза",
        "stop": "⏹ Стоп",
        "volume": "Громкость",
        "mute": "Выключить звук",
        "unmute": "Включить звук",
        "fullscreen": "⛶ Полный экран",
        "all_countries": "Все страны",
        "all_categories": "Все категории",
        "error_title": "Ошибка",
        "info_title": "Информация",
        "loading_db_failed": "Не удалось загрузить базу каналов:\n\n{message}",
        "database_error": "Ошибка загрузки базы.",
        "select_channel_first": "Сначала выберите канал в списке.",
        "no_stream_title": "Нет потока",
        "no_stream_text": "Для этого канала нет доступного потока.",
        "play_error_title": "Ошибка воспроизведения",
        "epg_loading": "Телепрограмма: загрузка...",
        "epg_none": "Телепрограмма: нет данных EPG для этого канала.",
        "epg_header": "Телепрограмма:",
        "epg_now": "СЕЙЧАС",
        "epg_next": "ДАЛЕЕ",
        "count_channels": "Каналов: {total}",
        "count_limited": "Показано {shown} из {total} каналов — уточните фильтры.",
        "player_unavailable": (
            "Плеер libmpv недоступен.\n\n"
            "Ubuntu/Debian:  sudo apt install libmpv2\n"
            "Windows: положите libmpv-2.dll рядом с приложением.\n\n"
            "Подробности: {error}"
        ),
        "player_hint": "Дважды щёлкните канал в списке, чтобы начать воспроизведение.",
        "mpv_unavailable": "libmpv / python-mpv недоступен. {error}",
        "mpv_locale_error": (
            "Не удалось инициализировать libmpv (LC_NUMERIC не установлен "
            "в 'C'). Запустите: LC_ALL=C omnity"
        ),
        "progress_downloading": "Загрузка {name}...",
        "progress_done": "Готово.",
        "download_cancelled": "загрузка отменена",
        "download_stopped": "отменено",
        "download_failed": "Не удалось скачать {name}: {error}",
    },
    "fr": {
        "app_title": "OmniTV — TV en ligne gratuite",
        "language_label": "Langue :",
        "theme_label": "Thème :",
        "search_placeholder": "Rechercher une chaîne, une catégorie ou un pays...",
        "add_favorite": "☆ Ajouter aux favoris",
        "remove_favorite": "★ Retirer des favoris",
        "only_favorites": "Favoris uniquement",
        "loading_db": "Chargement de la base des chaînes...",
        "downloading_db": "Téléchargement de la base des chaînes...",
        "refresh_db": "Actualiser la base des chaînes",
        "no_channel": "Aucune chaîne en lecture.",
        "now_playing": "Lecture : {name}",
        "epg_prefix": "Programme TV : —",
        "play": "▶ Lire",
        "pause": "⏸ Pause",
        "stop": "⏹ Arrêter",
        "volume": "Volume",
        "mute": "Couper le son",
        "unmute": "Activer le son",
        "fullscreen": "⛶ Plein écran",
        "all_countries": "Tous les pays",
        "all_categories": "Toutes les catégories",
        "error_title": "Erreur",
        "info_title": "Information",
        "loading_db_failed": "Impossible de charger la base des chaînes :\n\n{message}",
        "database_error": "Erreur de chargement de la base.",
        "select_channel_first": "Sélectionnez d'abord une chaîne dans la liste.",
        "no_stream_title": "Aucun flux",
        "no_stream_text": "Cette chaîne n'a pas de flux disponible.",
        "play_error_title": "Erreur de lecture",
        "epg_loading": "Programme TV : chargement...",
        "epg_none": "Programme TV : aucune donnée EPG pour cette chaîne.",
        "epg_header": "Programme TV :",
        "epg_now": "MAINTENANT",
        "epg_next": "ENSUITE",
        "count_channels": "Chaînes : {total}",
        "count_limited": "{shown} chaînes sur {total} affichées — affinez les filtres.",
        "player_unavailable": (
            "Le lecteur libmpv est indisponible.\n\n"
            "Ubuntu/Debian :  sudo apt install libmpv2\n"
            "Windows : placez libmpv-2.dll à côté de l'application.\n\n"
            "Détails : {error}"
        ),
        "player_hint": "Double-cliquez sur une chaîne dans la liste pour lancer la lecture.",
        "mpv_unavailable": "libmpv / python-mpv est indisponible. {error}",
        "mpv_locale_error": (
            "Impossible d'initialiser libmpv (LC_NUMERIC n'est pas défini "
            "sur 'C'). Essayez : LC_ALL=C omnity"
        ),
        "progress_downloading": "Téléchargement de {name}...",
        "progress_done": "Terminé.",
        "download_cancelled": "téléchargement annulé",
        "download_stopped": "annulé",
        "download_failed": "Échec du téléchargement de {name} : {error}",
    },
    "it": {
        "app_title": "OmniTV — TV online gratuita",
        "language_label": "Lingua:",
        "theme_label": "Tema:",
        "search_placeholder": "Cerca canale, categoria o paese...",
        "add_favorite": "☆ Aggiungi ai preferiti",
        "remove_favorite": "★ Rimuovi dai preferiti",
        "only_favorites": "Solo preferiti",
        "loading_db": "Caricamento del database dei canali...",
        "downloading_db": "Download del database dei canali...",
        "refresh_db": "Aggiorna il database dei canali",
        "no_channel": "Nessun canale in riproduzione.",
        "now_playing": "Riproduzione: {name}",
        "epg_prefix": "Guida TV: —",
        "play": "▶ Riproduci",
        "pause": "⏸ Pausa",
        "stop": "⏹ Stop",
        "volume": "Volume",
        "mute": "Disattiva audio",
        "unmute": "Attiva audio",
        "fullscreen": "⛶ Schermo intero",
        "all_countries": "Tutti i paesi",
        "all_categories": "Tutte le categorie",
        "error_title": "Errore",
        "info_title": "Informazioni",
        "loading_db_failed": "Impossibile caricare il database dei canali:\n\n{message}",
        "database_error": "Errore nel caricamento del database.",
        "select_channel_first": "Seleziona prima un canale dall'elenco.",
        "no_stream_title": "Nessun flusso",
        "no_stream_text": "Questo canale non ha un flusso disponibile.",
        "play_error_title": "Errore di riproduzione",
        "epg_loading": "Guida TV: caricamento...",
        "epg_none": "Guida TV: nessun dato EPG per questo canale.",
        "epg_header": "Guida TV:",
        "epg_now": "ORA",
        "epg_next": "POI",
        "count_channels": "Canali: {total}",
        "count_limited": "Mostrati {shown} di {total} canali — restringi i filtri.",
        "player_unavailable": (
            "Il lettore libmpv non è disponibile.\n\n"
            "Ubuntu/Debian:  sudo apt install libmpv2\n"
            "Windows: metti libmpv-2.dll accanto all'applicazione.\n\n"
            "Dettagli: {error}"
        ),
        "player_hint": "Fai doppio clic su un canale nell'elenco per iniziare la riproduzione.",
        "mpv_unavailable": "libmpv / python-mpv non è disponibile. {error}",
        "mpv_locale_error": (
            "Impossibile inizializzare libmpv (LC_NUMERIC non è impostato "
            "su 'C'). Prova: LC_ALL=C omnity"
        ),
        "progress_downloading": "Download di {name}...",
        "progress_done": "Fatto.",
        "download_cancelled": "download annullato",
        "download_stopped": "annullato",
        "download_failed": "Download di {name} non riuscito: {error}",
    },
    "es": {
        "app_title": "OmniTV — TV online gratis",
        "language_label": "Idioma:",
        "theme_label": "Tema:",
        "search_placeholder": "Buscar canal, categoría o país...",
        "add_favorite": "☆ Añadir a favoritos",
        "remove_favorite": "★ Quitar de favoritos",
        "only_favorites": "Solo favoritos",
        "loading_db": "Cargando la base de canales...",
        "downloading_db": "Descargando la base de canales...",
        "refresh_db": "Actualizar la base de canales",
        "no_channel": "No se está reproduciendo ningún canal.",
        "now_playing": "Reproduciendo: {name}",
        "epg_prefix": "Guía TV: —",
        "play": "▶ Reproducir",
        "pause": "⏸ Pausa",
        "stop": "⏹ Detener",
        "volume": "Volumen",
        "mute": "Silenciar",
        "unmute": "Activar sonido",
        "fullscreen": "⛶ Pantalla completa",
        "all_countries": "Todos los países",
        "all_categories": "Todas las categorías",
        "error_title": "Error",
        "info_title": "Información",
        "loading_db_failed": "No se pudo cargar la base de canales:\n\n{message}",
        "database_error": "Error al cargar la base de datos.",
        "select_channel_first": "Primero selecciona un canal de la lista.",
        "no_stream_title": "Sin transmisión",
        "no_stream_text": "Este canal no tiene ninguna transmisión disponible.",
        "play_error_title": "Error de reproducción",
        "epg_loading": "Guía TV: cargando...",
        "epg_none": "Guía TV: no hay datos EPG para este canal.",
        "epg_header": "Guía TV:",
        "epg_now": "AHORA",
        "epg_next": "DESPUÉS",
        "count_channels": "Canales: {total}",
        "count_limited": "Mostrando {shown} de {total} canales — reduce los filtros.",
        "player_unavailable": (
            "El reproductor libmpv no está disponible.\n\n"
            "Ubuntu/Debian:  sudo apt install libmpv2\n"
            "Windows: coloca libmpv-2.dll junto a la aplicación.\n\n"
            "Detalles: {error}"
        ),
        "player_hint": "Haz doble clic en un canal de la lista para empezar la reproducción.",
        "mpv_unavailable": "libmpv / python-mpv no está disponible. {error}",
        "mpv_locale_error": (
            "No se pudo inicializar libmpv (LC_NUMERIC no está establecido "
            "en 'C'). Prueba: LC_ALL=C omnity"
        ),
        "progress_downloading": "Descargando {name}...",
        "progress_done": "Listo.",
        "download_cancelled": "descarga cancelada",
        "download_stopped": "cancelado",
        "download_failed": "No se pudo descargar {name}: {error}",
    },
}

_EXTRA_TRANSLATIONS = {
    "pl": {
        "country_filter": "Filtruj według kraju",
        "category_filter": "Filtruj według kategorii",
        "add_custom_channel": "＋ Dodaj kanał / stream",
        "remove_custom_channel": "Usuń własny",
        "custom_channel_name": "Nazwa",
        "custom_channel_name_hint": "np. Mój kanał",
        "custom_channel_url": "Adres URL",
        "custom_url_invalid": "Podaj nazwę i poprawny adres HTTP/HTTPS bez danych logowania.",
        "resolving_stream": "Łączenie z serwisem streamingowym…",
        "stream_resolution_failed": "Nie udało się otworzyć tego strumienia:\n\n{error}",
        "minimize": "Minimalizuj",
        "maximize": "Maksymalizuj",
        "restore": "Przywróć",
        "close": "Zamknij",
        "subtitles_off": "💬 Napisy",
        "subtitles_on": "💬 Napisy: {lang}",
        "subtitles_waiting": "Napisy: szukam ścieżki...",
        "subtitles_none": "Napisy: ten kanał nie udostępnia napisów.",
        "subtitles_error": "Napisy: nie udało się przetłumaczyć.",
        "subtitles_select_first": "Najpierw włącz kanał, aby użyć napisów.",
        "record": "⏺ Nagraj",
        "stop_recording": "⏹ Zatrzymaj zapis",
        "recording": "Nagrywanie: {name}",
        "recording_saved": "Zapisano: {name}",
        "recording_failed": "Nie udało się nagrać:\n\n{error}",
        "recording_unavailable": (
            "Nagrywanie wymaga ffmpeg.\n\n"
            "Ubuntu/Debian:  sudo apt install ffmpeg\n"
            "Fedora:  sudo dnf install ffmpeg"
        ),
        "recording_requires_playback": "Najpierw odtwórz kanał, aby go nagrać.",
        "recording_fallback": "AVI nie obsługuje tego strumienia — zapisuję MKV: {name}",
    },
    "en": {
        "country_filter": "Filter by country",
        "category_filter": "Filter by category",
        "add_custom_channel": "＋ Add channel / stream",
        "remove_custom_channel": "Remove custom",
        "custom_channel_name": "Name",
        "custom_channel_name_hint": "e.g. My channel",
        "custom_channel_url": "URL",
        "custom_url_invalid": "Enter a name and a valid HTTP/HTTPS URL without credentials.",
        "resolving_stream": "Connecting to streaming service…",
        "stream_resolution_failed": "Could not open this stream:\n\n{error}",
        "minimize": "Minimize",
        "maximize": "Maximize",
        "restore": "Restore",
        "close": "Close",
        "subtitles_off": "💬 Subtitles",
        "subtitles_on": "💬 Subtitles: {lang}",
        "subtitles_waiting": "Subtitles: looking for a track...",
        "subtitles_none": "Subtitles: this channel does not provide subtitles.",
        "subtitles_error": "Subtitles: translation failed.",
        "subtitles_select_first": "Start a channel first to use subtitles.",
        "record": "⏺ Record",
        "stop_recording": "⏹ Stop recording",
        "recording": "Recording: {name}",
        "recording_saved": "Saved: {name}",
        "recording_failed": "Recording failed:\n\n{error}",
        "recording_unavailable": (
            "Recording requires ffmpeg.\n\n"
            "Ubuntu/Debian:  sudo apt install ffmpeg\n"
            "Fedora:  sudo dnf install ffmpeg"
        ),
        "recording_requires_playback": "Start a channel first to record it.",
        "recording_fallback": "AVI does not support this stream — saving MKV: {name}",
    },
    "de": {
        "country_filter": "Nach Land filtern",
        "category_filter": "Nach Kategorie filtern",
        "add_custom_channel": "＋ Sender / Stream hinzufügen",
        "remove_custom_channel": "Eigenen entfernen",
        "custom_channel_name": "Name",
        "custom_channel_name_hint": "z. B. Mein Sender",
        "custom_channel_url": "URL",
        "custom_url_invalid": "Gib einen Namen und eine gültige HTTP/HTTPS-URL ohne Zugangsdaten ein.",
        "resolving_stream": "Verbindung zum Streamingdienst…",
        "stream_resolution_failed": "Stream konnte nicht geöffnet werden:\n\n{error}",
        "minimize": "Minimieren",
        "maximize": "Maximieren",
        "restore": "Wiederherstellen",
        "close": "Schließen",
        "subtitles_off": "💬 Untertitel",
        "subtitles_on": "💬 Untertitel: {lang}",
        "subtitles_waiting": "Untertitel: Suche nach Spur...",
        "subtitles_none": "Untertitel: Dieser Sender bietet keine Untertitel.",
        "subtitles_error": "Untertitel: Übersetzung fehlgeschlagen.",
        "subtitles_select_first": "Starte zuerst einen Sender, um Untertitel zu nutzen.",
        "record": "⏺ Aufnehmen",
        "stop_recording": "⏹ Aufnahme stoppen",
        "recording": "Aufnahme: {name}",
        "recording_saved": "Gespeichert: {name}",
        "recording_failed": "Aufnahme fehlgeschlagen:\n\n{error}",
        "recording_unavailable": (
            "Für die Aufnahme wird ffmpeg benötigt.\n\n"
            "Ubuntu/Debian:  sudo apt install ffmpeg\n"
            "Fedora:  sudo dnf install ffmpeg"
        ),
        "recording_requires_playback": "Starte zuerst einen Sender, um ihn aufzunehmen.",
        "recording_fallback": "AVI unterstützt diesen Stream nicht — speichere MKV: {name}",
    },
    "ru": {
        "country_filter": "Фильтр по стране",
        "category_filter": "Фильтр по категории",
        "add_custom_channel": "＋ Добавить канал / поток",
        "remove_custom_channel": "Удалить свой",
        "custom_channel_name": "Название",
        "custom_channel_name_hint": "например, Мой канал",
        "custom_channel_url": "URL",
        "custom_url_invalid": "Укажите название и корректный HTTP/HTTPS URL без данных входа.",
        "resolving_stream": "Подключение к потоковому сервису…",
        "stream_resolution_failed": "Не удалось открыть поток:\n\n{error}",
        "minimize": "Свернуть",
        "maximize": "Развернуть",
        "restore": "Восстановить",
        "close": "Закрыть",
        "subtitles_off": "💬 Субтитры",
        "subtitles_on": "💬 Субтитры: {lang}",
        "subtitles_waiting": "Субтитры: поиск дорожки...",
        "subtitles_none": "Субтитры: этот канал не предоставляет субтитры.",
        "subtitles_error": "Субтитры: не удалось перевести.",
        "subtitles_select_first": "Сначала запустите канал, чтобы включить субтитры.",
        "record": "⏺ Записать",
        "stop_recording": "⏹ Остановить запись",
        "recording": "Запись: {name}",
        "recording_saved": "Сохранено: {name}",
        "recording_failed": "Не удалось записать:\n\n{error}",
        "recording_unavailable": (
            "Для записи требуется ffmpeg.\n\n"
            "Ubuntu/Debian:  sudo apt install ffmpeg\n"
            "Fedora:  sudo dnf install ffmpeg"
        ),
        "recording_requires_playback": "Сначала запустите канал, чтобы записать его.",
        "recording_fallback": "AVI не поддерживает этот поток — сохраняю MKV: {name}",
    },
    "fr": {
        "country_filter": "Filtrer par pays",
        "category_filter": "Filtrer par catégorie",
        "add_custom_channel": "＋ Ajouter une chaîne / un flux",
        "remove_custom_channel": "Supprimer le flux perso",
        "custom_channel_name": "Nom",
        "custom_channel_name_hint": "p. ex. Ma chaîne",
        "custom_channel_url": "URL",
        "custom_url_invalid": "Saisissez un nom et une URL HTTP/HTTPS valide sans identifiants.",
        "resolving_stream": "Connexion au service de streaming…",
        "stream_resolution_failed": "Impossible d'ouvrir ce flux :\n\n{error}",
        "minimize": "Réduire",
        "maximize": "Agrandir",
        "restore": "Restaurer",
        "close": "Fermer",
        "subtitles_off": "💬 Sous-titres",
        "subtitles_on": "💬 Sous-titres : {lang}",
        "subtitles_waiting": "Sous-titres : recherche d'une piste...",
        "subtitles_none": "Sous-titres : cette chaîne ne fournit pas de sous-titres.",
        "subtitles_error": "Sous-titres : échec de la traduction.",
        "subtitles_select_first": "Lancez d'abord une chaîne pour utiliser les sous-titres.",
        "record": "⏺ Enregistrer",
        "stop_recording": "⏹ Arrêter l'enregistrement",
        "recording": "Enregistrement : {name}",
        "recording_saved": "Enregistré : {name}",
        "recording_failed": "Échec de l'enregistrement :\n\n{error}",
        "recording_unavailable": (
            "L'enregistrement nécessite ffmpeg.\n\n"
            "Ubuntu/Debian :  sudo apt install ffmpeg\n"
            "Fedora :  sudo dnf install ffmpeg"
        ),
        "recording_requires_playback": "Lancez d'abord une chaîne pour l'enregistrer.",
        "recording_fallback": "AVI ne prend pas en charge ce flux — sauvegarde en MKV : {name}",
    },
    "it": {
        "country_filter": "Filtra per paese",
        "category_filter": "Filtra per categoria",
        "add_custom_channel": "＋ Aggiungi canale / stream",
        "remove_custom_channel": "Rimuovi personalizzato",
        "custom_channel_name": "Nome",
        "custom_channel_name_hint": "es. Il mio canale",
        "custom_channel_url": "URL",
        "custom_url_invalid": "Inserisci un nome e un URL HTTP/HTTPS valido senza credenziali.",
        "resolving_stream": "Connessione al servizio streaming…",
        "stream_resolution_failed": "Impossibile aprire questo stream:\n\n{error}",
        "minimize": "Riduci a icona",
        "maximize": "Ingrandisci",
        "restore": "Ripristina",
        "close": "Chiudi",
        "subtitles_off": "💬 Sottotitoli",
        "subtitles_on": "💬 Sottotitoli: {lang}",
        "subtitles_waiting": "Sottotitoli: ricerca della traccia...",
        "subtitles_none": "Sottotitoli: questo canale non fornisce sottotitoli.",
        "subtitles_error": "Sottotitoli: traduzione non riuscita.",
        "subtitles_select_first": "Avvia prima un canale per usare i sottotitoli.",
        "record": "⏺ Registra",
        "stop_recording": "⏹ Ferma registrazione",
        "recording": "Registrazione: {name}",
        "recording_saved": "Salvato: {name}",
        "recording_failed": "Registrazione non riuscita:\n\n{error}",
        "recording_unavailable": (
            "La registrazione richiede ffmpeg.\n\n"
            "Ubuntu/Debian:  sudo apt install ffmpeg\n"
            "Fedora:  sudo dnf install ffmpeg"
        ),
        "recording_requires_playback": "Avvia prima un canale per registrarlo.",
        "recording_fallback": "AVI non supporta questo flusso — salvo in MKV: {name}",
    },
    "es": {
        "country_filter": "Filtrar por país",
        "category_filter": "Filtrar por categoría",
        "add_custom_channel": "＋ Añadir canal / stream",
        "remove_custom_channel": "Quitar personalizado",
        "custom_channel_name": "Nombre",
        "custom_channel_name_hint": "p. ej., Mi canal",
        "custom_channel_url": "URL",
        "custom_url_invalid": "Introduce un nombre y una URL HTTP/HTTPS válida sin credenciales.",
        "resolving_stream": "Conectando al servicio de streaming…",
        "stream_resolution_failed": "No se pudo abrir este stream:\n\n{error}",
        "minimize": "Minimizar",
        "maximize": "Maximizar",
        "restore": "Restaurar",
        "close": "Cerrar",
        "subtitles_off": "💬 Subtítulos",
        "subtitles_on": "💬 Subtítulos: {lang}",
        "subtitles_waiting": "Subtítulos: buscando una pista...",
        "subtitles_none": "Subtítulos: este canal no ofrece subtítulos.",
        "subtitles_error": "Subtítulos: no se pudo traducir.",
        "subtitles_select_first": "Primero inicia un canal para usar los subtítulos.",
        "record": "⏺ Grabar",
        "stop_recording": "⏹ Detener grabación",
        "recording": "Grabando: {name}",
        "recording_saved": "Guardado: {name}",
        "recording_failed": "No se pudo grabar:\n\n{error}",
        "recording_unavailable": (
            "La grabación requiere ffmpeg.\n\n"
            "Ubuntu/Debian:  sudo apt install ffmpeg\n"
            "Fedora:  sudo dnf install ffmpeg"
        ),
        "recording_requires_playback": "Primero inicia un canal para grabarlo.",
        "recording_fallback": "AVI no admite este flujo — guardando MKV: {name}",
    },
}

for _code, _values in _EXTRA_TRANSLATIONS.items():
    TRANSLATIONS[_code].update(_values)

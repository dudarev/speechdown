from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class Timestamp:
    value: datetime

    @staticmethod
    def from_isoformat(isoformat: str) -> "Timestamp":
        return Timestamp(datetime.fromisoformat(isoformat))


# https://github.com/openai/whisper/blob/ba3f3cd54b0e5b8ce1ab3de13e32122d0d5f98ab/whisper/tokenizer.py#L10
LANGUAGES = {
    "en": "english",
    "zh": "chinese",
    "de": "german",
    "es": "spanish",
    "ru": "russian",
    "ko": "korean",
    "fr": "french",
    "ja": "japanese",
    "pt": "portuguese",
    "tr": "turkish",
    "pl": "polish",
    "ca": "catalan",
    "nl": "dutch",
    "ar": "arabic",
    "sv": "swedish",
    "it": "italian",
    "id": "indonesian",
    "hi": "hindi",
    "fi": "finnish",
    "vi": "vietnamese",
    "he": "hebrew",
    "uk": "ukrainian",
    "el": "greek",
    "ms": "malay",
    "cs": "czech",
    "ro": "romanian",
    "da": "danish",
    "hu": "hungarian",
    "ta": "tamil",
    "no": "norwegian",
    "th": "thai",
    "ur": "urdu",
    "hr": "croatian",
    "bg": "bulgarian",
    "lt": "lithuanian",
    "la": "latin",
    "mi": "maori",
    "ml": "malayalam",
    "cy": "welsh",
    "sk": "slovak",
    "te": "telugu",
    "fa": "persian",
    "lv": "latvian",
    "bn": "bengali",
    "sr": "serbian",
    "az": "azerbaijani",
    "sl": "slovenian",
    "kn": "kannada",
    "et": "estonian",
    "mk": "macedonian",
    "br": "breton",
    "eu": "basque",
    "is": "icelandic",
    "hy": "armenian",
    "ne": "nepali",
    "mn": "mongolian",
    "bs": "bosnian",
    "kk": "kazakh",
    "sq": "albanian",
    "sw": "swahili",
    "gl": "galician",
    "mr": "marathi",
    "pa": "punjabi",
    "si": "sinhala",
    "km": "khmer",
    "sn": "shona",
    "yo": "yoruba",
    "so": "somali",
    "af": "afrikaans",
    "oc": "occitan",
    "ka": "georgian",
    "be": "belarusian",
    "tg": "tajik",
    "sd": "sindhi",
    "gu": "gujarati",
    "am": "amharic",
    "yi": "yiddish",
    "lo": "lao",
    "uz": "uzbek",
    "fo": "faroese",
    "ht": "haitian creole",
    "ps": "pashto",
    "tk": "turkmen",
    "nn": "nynorsk",
    "mt": "maltese",
    "sa": "sanskrit",
    "lb": "luxembourgish",
    "my": "myanmar",
    "bo": "tibetan",
    "tl": "tagalog",
    "mg": "malagasy",
    "as": "assamese",
    "tt": "tatar",
    "haw": "hawaiian",
    "ln": "lingala",
    "ha": "hausa",
    "ba": "bashkir",
    "jw": "javanese",
    "su": "sundanese",
    "yue": "cantonese",
}

# language code lookup by name, with a few language aliases
TO_LANGUAGE_CODE = {
    **{language: code for code, language in LANGUAGES.items()},
    "burmese": "my",
    "valencian": "ca",
    "flemish": "nl",
    "haitian": "ht",
    "letzeburgesch": "lb",
    "pushto": "ps",
    "panjabi": "pa",
    "moldavian": "ro",
    "moldovan": "ro",
    "sinhalese": "si",
    "castilian": "es",
    "mandarin": "zh",
}


@dataclass(frozen=True)
class Language:
    code: str

    @classmethod
    def from_code(cls, code: str) -> "Language":
        if code in LANGUAGES:
            return cls(code)
        else:
            raise ValueError(f"Invalid language code: {code}")

    def __str__(self):
        return self.code


class MetricSource(Enum):
    """Source of the transcription metrics"""

    WHISPER = auto()
    CUSTOM = auto()
    OTHER = auto()


@dataclass(frozen=True)
class TranscriptionMetrics:
    """
    Value object representing transcription metrics

    Example how raw data looks like from whisper:

    {
        'language': 'en',
        'segments': [
            {
                'avg_logprob': -0.8121594429016114,
                'compression_ratio': 0.42857142857142855,
                'end': 2.0,
                'id': 0,
                'no_speech_prob': 0.2180071920156479,
                'seek': 0,
                'start': 0.0,
                'temperature': 0.0,
                'text': ' Dust 2',
                'tokens': [50364, 26483, 568, 50464]
            }
        ],
        'text': ' Dust 2'
    }
    """

    # Information about the transcription process
    model_name: Optional[str] = None
    transcription_time_seconds: Optional[float] = None

    # Common metrics with explicit fields

    # The confidence score is a single value that allows comparison between different transcriptions.
    # It's derived from the model's internal metrics (typically avg_logprob values) and represents
    # the overall reliability of the transcription. Higher values (closer to 0) indicate higher confidence.
    # This is the primary metric used when selecting the "best" transcription among alternatives.
    confidence: Optional[float] = None
    audio_duration_seconds: Optional[float] = None
    word_count: Optional[int] = None
    words_per_second: Optional[float] = None
    language_detection_confidence: Optional[float] = None

    # Speech quality metrics
    avg_logprob_mean: Optional[float] = None
    compression_ratio_mean: Optional[float] = None
    no_speech_prob_mean: Optional[float] = None

    # Metadata
    source: MetricSource = MetricSource.WHISPER

    # Extensibility field for additional metrics
    additional_metrics: Dict[str, Any] = field(default_factory=dict)

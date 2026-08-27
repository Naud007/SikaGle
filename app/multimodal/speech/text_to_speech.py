import base64
import binascii
import os
import re
import subprocess
import tempfile
import wave
from pathlib import Path

from google import genai
from google.genai import types

from app.multimodal.models.speech_response import (
    SpeechResponse,
)
from app.multimodal.speech.voice_selector import (
    VoiceSelector,
)


class TextToSpeech:
    """
    Génère un fichier audio à partir d'un texte, en utilisant
    le modèle de synthèse vocale natif de Gemini.

    Gemini TTS ne produit que de l'audio brut (PCM). Ce service
    l'écrit d'abord dans un fichier WAV, puis le convertit en
    MP3 (format accepté par l'API WhatsApp Cloud) grâce à
    imageio-ffmpeg, qui embarque son propre binaire ffmpeg
    (aucune installation système requise, fonctionne pareil
    en local et sur Render).

    Limite connue : ce modèle ne supporte officiellement que
    le français parmi les langues de SikaGlé (pas Fon, Yoruba
    ni Dendi pour l'instant).
    """

    MODEL = "gemini-3.1-flash-tts-preview"

    CHANNELS = 1
    DEFAULT_SAMPLE_RATE = 24000
    SAMPLE_WIDTH = 2  # 16 bits

    def __init__(self):

        self.client = genai.Client()

        self.voice_selector = VoiceSelector()

    def synthesize(
        self,
        text: str,
        language: str = "fr",
    ) -> SpeechResponse:

        if not text or not text.strip():

            raise ValueError(
                "Le texte à synthétiser est vide."
            )

        voice = self.voice_selector.select(
            language
        )

        response = self.client.models.generate_content(
            model=self.MODEL,
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice
                        )
                    )
                ),
            ),
        )

        pcm_data = None

        part_mime_type = ""

        parts = (
            response
            .candidates[0]
            .content
            .parts
        )

        for part in parts:

            inline_data = getattr(
                part,
                "inline_data",
                None,
            )

            if inline_data is None:
                continue

            candidate_mime_type = (
                getattr(
                    inline_data,
                    "mime_type",
                    "",
                )
                or ""
            )

            if candidate_mime_type.startswith(
                "audio/"
            ):

                pcm_data = (
                    inline_data.data
                )

                part_mime_type = (
                    candidate_mime_type
                )

                break

        if not pcm_data:

            raise ValueError(
                "Gemini n'a retourné aucune "
                "partie audio exploitable."
            )

        # =====================================================
        # DÉCODAGE DES DONNÉES AUDIO
        #
        # NOTE :
        #
        # Le SDK google-genai renvoie parfois un objet `bytes`
        # dont le CONTENU est en réalité du texte base64 non
        # décodé (et non de l'audio binaire brut). On tente
        # donc systématiquement un décodage base64, et on ne
        # garde les octets tels quels que si ce décodage
        # échoue (preuve qu'il s'agissait bien de vraies
        # données binaires).
        # =====================================================

        try:

            if isinstance(
                pcm_data,
                bytes,
            ):

                text_candidate = (
                    pcm_data.decode(
                        "ascii"
                    )
                )

            else:

                text_candidate = pcm_data

            pcm_data = base64.b64decode(
                text_candidate,
                validate=True,
            )

        except (
            UnicodeDecodeError,
            binascii.Error,
            ValueError,
        ):

            if isinstance(
                pcm_data,
                str,
            ):

                pcm_data = base64.b64decode(
                    pcm_data
                )

        sample_rate = self._parse_sample_rate(
            part_mime_type
        )

        wav_fd, wav_path_str = tempfile.mkstemp(
            suffix=".wav"
        )

        os.close(wav_fd)

        wav_path = Path(wav_path_str)

        with wave.open(
            wav_path_str,
            "wb",
        ) as wf:

            wf.setnchannels(
                self.CHANNELS
            )

            wf.setsampwidth(
                self.SAMPLE_WIDTH
            )

            wf.setframerate(
                sample_rate
            )

            wf.writeframes(
                pcm_data
            )

        mp3_path = wav_path.with_suffix(
            ".mp3"
        )

        self._convert_to_mp3(
            wav_path,
            mp3_path,
        )

        wav_path.unlink(
            missing_ok=True
        )

        return SpeechResponse(
            audio_path=mp3_path,
            language=language,
            voice=voice,
            speed=1.0,
        )

    def _parse_sample_rate(
        self,
        mime_type: str,
    ) -> int:

        match = re.search(
            r"rate=(\d+)",
            mime_type or "",
        )

        if match:

            return int(
                match.group(1)
            )

        return (
            self.DEFAULT_SAMPLE_RATE
        )

    def _convert_to_mp3(
        self,
        wav_path: Path,
        mp3_path: Path,
    ) -> None:

        import imageio_ffmpeg

        ffmpeg_exe = (
            imageio_ffmpeg.get_ffmpeg_exe()
        )

        subprocess.run(
            [
                ffmpeg_exe,
                "-y",
                "-i",
                str(wav_path),
                "-codec:a",
                "libmp3lame",
                "-qscale:a",
                "2",
                str(mp3_path),
            ],
            check=True,
            capture_output=True,
        )
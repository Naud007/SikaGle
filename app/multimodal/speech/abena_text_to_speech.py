import base64
import os
import re
import subprocess
import tempfile
import wave
from pathlib import Path

import requests

from app.core.retry import call_with_retry
from app.multimodal.models.speech_response import (
    SpeechResponse,
)


class AbenaTextToSpeech:
    """
    Synthèse vocale en Yoruba via l'API Abena AI (voix
    'folami_yor'). Réutilisée uniquement pour les langues que
    Gemini TTS ne couvre pas (voir décision du 28/08/2026).
    """

    API_URL = (
        "https://abena.mobobi.com/playground/api/v1"
        "/tts/synthesize/"
    )

    # L'API Abena limite chaque requête à 500 caractères.
    MAX_CHARS_PER_REQUEST = 480

    VOICE_BY_LANGUAGE = {
        "yo": "folami_yor",
    }

    def synthesize(
        self,
        text: str,
        language: str = "yo",
    ) -> SpeechResponse:

        if not text or not text.strip():

            raise ValueError(
                "Le texte à synthétiser est vide."
            )

        voice = self.VOICE_BY_LANGUAGE.get(
            language
        )

        if not voice:

            raise ValueError(
                "Aucune voix Abena AI configurée "
                f"pour la langue : {language}"
            )

        chunks = self._split_text(
            text
        )

        wav_chunks: list[bytes] = []

        for chunk in chunks:

            wav_chunks.append(
                self._synthesize_chunk(
                    chunk,
                    voice,
                )
            )

        wav_path = self._concatenate_wav(
            wav_chunks
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

    # =========================================================
    # DÉCOUPAGE DU TEXTE (limite 500 caractères par requête)
    # =========================================================

    def _split_text(
        self,
        text: str,
    ) -> list[str]:

        sentences = re.split(
            r"(?<=[.!?])\s+",
            text.strip(),
        )

        chunks: list[str] = []

        current = ""

        for sentence in sentences:

            candidate = (
                f"{current} {sentence}".strip()
                if current
                else sentence
            )

            if (
                len(candidate)
                <= self.MAX_CHARS_PER_REQUEST
            ):

                current = candidate

            else:

                if current:

                    chunks.append(
                        current
                    )

                current = sentence[
                    :self.MAX_CHARS_PER_REQUEST
                ]

        if current:

            chunks.append(
                current
            )

        return chunks or [
            text[:self.MAX_CHARS_PER_REQUEST]
        ]

    # =========================================================
    # APPEL API ABENA (une requête = un morceau de texte)
    # =========================================================

    def _synthesize_chunk(
        self,
        chunk_text: str,
        voice: str,
    ) -> bytes:

        def _call():

            response = requests.post(
                self.API_URL,
                json={
                    "text": chunk_text,
                    "voice": voice,
                    "speed": 1.0,
                },
                timeout=60,
            )

            if response.status_code != 200:

                raise RuntimeError(
                    "Abena AI a répondu avec le "
                    f"statut {response.status_code} : "
                    f"{response.text}"
                )

            return response.json()

        data = call_with_retry(
            _call
        )

        audio_base64 = data.get(
            "audio_base64"
        )

        if not audio_base64:

            raise ValueError(
                "Abena AI n'a retourné aucun "
                "audio exploitable."
            )

        return base64.b64decode(
            audio_base64
        )

    # =========================================================
    # CONCATÉNATION DES MORCEAUX WAV
    # =========================================================

    def _concatenate_wav(
        self,
        wav_chunks: list[bytes],
    ) -> Path:

        wav_fd, wav_path_str = tempfile.mkstemp(
            suffix=".wav"
        )

        os.close(wav_fd)

        wav_path = Path(wav_path_str)

        output_wave = None

        for chunk_bytes in wav_chunks:

            chunk_temp_fd, chunk_temp_path = (
                tempfile.mkstemp(
                    suffix=".wav"
                )
            )

            os.close(
                chunk_temp_fd
            )

            Path(
                chunk_temp_path
            ).write_bytes(
                chunk_bytes
            )

            with wave.open(
                chunk_temp_path,
                "rb",
            ) as chunk_wave:

                if output_wave is None:

                    output_wave = wave.open(
                        wav_path_str,
                        "wb",
                    )

                    output_wave.setparams(
                        chunk_wave.getparams()
                    )

                output_wave.writeframes(
                    chunk_wave.readframes(
                        chunk_wave.getnframes()
                    )
                )

            Path(
                chunk_temp_path
            ).unlink(
                missing_ok=True
            )

        if output_wave:

            output_wave.close()

        return wav_path

    # =========================================================
    # CONVERSION WAV → MP3 (format accepté par WhatsApp)
    # =========================================================

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
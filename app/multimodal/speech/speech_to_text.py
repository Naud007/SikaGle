import base64
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
        # DIAGNOSTIC TEMPORAIRE GEMINI TTS
        # =====================================================

        print("🔬 TTS DEBUG — nombre de parts :", len(parts))
        print("🔬 TTS DEBUG — mime_type :", part_mime_type)
        print("🔬 TTS DEBUG — type données :", type(pcm_data))
        print("🔬 TTS DEBUG — taille données :", len(pcm_data))

        if isinstance(pcm_data, bytes):
            print(
                "🔬 TTS DEBUG — premiers octets :",
                pcm_data[:32].hex(),
            )
        elif isinstance(pcm_data, str):
            print(
                "🔬 TTS DEBUG — premiers caractères :",
                pcm_data[:80],
            )

        # =====================================================
        # DÉCODAGE BASE64 SI NÉCESSAIRE
        # =====================================================

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
import base64
import os
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

    # Paramètres audio de sortie de Gemini TTS
    CHANNELS = 1
    SAMPLE_RATE = 24000
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

        pcm_data = (
            response
            .candidates[0]
            .content
            .parts[0]
            .inline_data
            .data
        )

        if not pcm_data:

            raise ValueError(
                "Gemini n'a retourné aucun audio."
            )

        # =====================================================
        # CORRECTIF (bruit statique) :
        #
        # Selon la version du SDK, inline_data.data peut être
        # retourné soit comme des octets bruts (bytes) déjà
        # décodés, soit comme une chaîne de texte encodée en
        # base64. Écrire une chaîne base64 directement comme
        # si c'était du PCM produit un bruit statique/blanc au
        # lieu de la voix (symptôme confirmé, problème connu
        # du SDK google-genai — voir issue #837 sur son dépôt
        # GitHub officiel). On détecte donc le type reçu et on
        # décode si nécessaire.
        # =====================================================

        if isinstance(
            pcm_data,
            str,
        ):

            pcm_data = base64.b64decode(
                pcm_data
            )

        # =====================================================
        # ÉCRITURE DU FICHIER WAV
        # =====================================================

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
                self.SAMPLE_RATE
            )

            wf.writeframes(
                pcm_data
            )

        # =====================================================
        # CONVERSION EN MP3 (format accepté par WhatsApp)
        # =====================================================

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
    # CONVERSION WAV → MP3
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
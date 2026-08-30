import requests

from app.core.retry import call_with_retry


# =============================================================
# CODES MÉTÉO OPEN-METEO (WMO) → DESCRIPTION SIMPLE EN FRANÇAIS
# =============================================================

WEATHER_CODE_DESCRIPTIONS = {
    0: "ciel dégagé",
    1: "plutôt dégagé",
    2: "partiellement nuageux",
    3: "ciel couvert",
    45: "brouillard",
    48: "brouillard givrant",
    51: "légère bruine",
    53: "bruine modérée",
    55: "forte bruine",
    61: "pluie légère",
    63: "pluie modérée",
    65: "forte pluie",
    80: "averses légères",
    81: "averses modérées",
    82: "fortes averses",
    95: "orage",
    96: "orage avec grêle légère",
    99: "orage avec forte grêle",
}


class WeatherService:
    """
    Récupère la météo actuelle pour une localisation donnée
    (texte libre, ex: "Savalou"), via Open-Meteo.

    NOTE (limite de licence) : Open-Meteo est gratuit pour un
    usage NON-COMMERCIAL, avec un plan payant disponible pour
    la production commerciale. Utilisé ici en phase MVP ; à
    revoir avant un lancement commercial réel.
    """

    GEOCODING_URL = (
        "https://geocoding-api.open-meteo.com/v1/search"
    )

    FORECAST_URL = (
        "https://api.open-meteo.com/v1/forecast"
    )

    # Code pays ISO du Bénin, utilisé pour prioriser les
    # résultats de géocodage plutôt que d'injecter "Bénin"
    # directement dans le texte recherché (voir correctif
    # ci-dessous).
    BENIN_COUNTRY_CODE = "BJ"

    def geocode(
        self,
        location_text: str,
    ) -> tuple[float, float] | None:
        """
        Convertit un nom de lieu (ex: "Savalou") en
        coordonnées (latitude, longitude). Retourne None si
        rien n'est trouvé, même après plusieurs variantes.

        NOTE (correctif définitif, 30/08/2026) :

        Deux problèmes cumulés ont été identifiés en test réel :

        1. L'API de géocodage Open-Meteo est sensible au trait
           d'union : "Abomey-Calavi" fonctionne mais "Abomey
           Calavi" (espace) échoue. On essaie donc plusieurs
           variantes de PONCTUATION DU NOM DE LIEU SEUL.

        2. Injecter le pays directement dans le texte recherché
           (ex: "Abomey calavi, Bénin") casse tout : remplacer
           les espaces par des tirets transforme aussi celui
           après la virgule ("Abomey-calavi,-Bénin"), ce qui
           n'est reconnu par aucune commune. Le nom de pays ne
           doit donc JAMAIS être concaténé au texte de
           recherche. À la place, on demande plusieurs résultats
           à l'API (count=5) et on choisit en priorité celui
           dont le country_code est "BJ" (Bénin), sans jamais
           construire de chaîne "Ville, Pays".

        location_text doit donc être UNIQUEMENT le nom de la
        commune (ex: "Abomey Calavi"), jamais suffixé par le
        pays — c'est cette méthode qui gère la priorité Bénin
        en interne.
        """

        if not location_text or not location_text.strip():

            return None

        # Si un appelant a quand même ajouté un pays après une
        # virgule (ex: ancien code, ou saisie utilisateur), on
        # ne garde que la partie avant la virgule : c'est le
        # nom de lieu seul qui doit être varié en tirets/espaces,
        # jamais la chaîne complète.
        city_only = (
            location_text
            .split(",")[0]
            .strip()
        )

        candidates = [
            city_only,
            city_only.replace(
                " ",
                "-",
            ),
            city_only.replace(
                "-",
                " ",
            ),
        ]

        candidates = list(
            dict.fromkeys(
                candidates
            )
        )

        for candidate in candidates:

            result = self._geocode_single(
                candidate
            )

            if result:

                return result

        return None

    def _geocode_single(
        self,
        location_text: str,
    ) -> tuple[float, float] | None:
        """
        Interroge l'API de géocodage pour UN texte donné, en
        demandant plusieurs résultats (count=5) et en
        choisissant en priorité celui situé au Bénin, plutôt
        que de se fier uniquement au premier résultat renvoyé.
        """

        def _call():

            return requests.get(
                self.GEOCODING_URL,
                params={
                    "name": location_text,
                    "count": 5,
                    "language": "fr",
                },
                timeout=15,
            )

        response = call_with_retry(
            _call
        )

        if response.status_code != 200:

            return None

        data = response.json()

        results = data.get(
            "results"
        )

        if not results:

            return None

        benin_match = next(
            (
                r
                for r in results
                if r.get("country_code")
                == self.BENIN_COUNTRY_CODE
            ),
            None,
        )

        best_match = (
            benin_match
            or results[0]
        )

        return (
            best_match["latitude"],
            best_match["longitude"],
        )

    def get_current_weather(
        self,
        latitude: float,
        longitude: float,
    ) -> dict | None:
        """
        Retourne les conditions météo actuelles pour des
        coordonnées données, ou None en cas d'échec.
        """

        def _call():

            return requests.get(
                self.FORECAST_URL,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": (
                        "temperature_2m,"
                        "relative_humidity_2m,"
                        "precipitation,"
                        "weather_code,"
                        "wind_speed_10m"
                    ),
                    "daily": (
                        "precipitation_probability_max,"
                        "precipitation_sum"
                    ),
                    "forecast_days": 1,
                    "timezone": "auto",
                },
                timeout=15,
            )

        response = call_with_retry(
            _call
        )

        if response.status_code != 200:

            return None

        data = response.json()

        current = data.get(
            "current",
            {},
        )

        daily = data.get(
            "daily",
            {},
        )

        weather_code = current.get(
            "weather_code"
        )

        return {
            "temperature_c": current.get(
                "temperature_2m"
            ),
            "humidity_percent": current.get(
                "relative_humidity_2m"
            ),
            "precipitation_mm_now": current.get(
                "precipitation"
            ),
            "wind_speed_kmh": current.get(
                "wind_speed_10m"
            ),
            "description": (
                WEATHER_CODE_DESCRIPTIONS.get(
                    weather_code,
                    "conditions inconnues",
                )
            ),
            "rain_probability_today_percent": (
                daily.get(
                    "precipitation_probability_max",
                    [None],
                )[0]
            ),
            "rain_total_today_mm": (
                daily.get(
                    "precipitation_sum",
                    [None],
                )[0]
            ),
        }

    def to_context_text(
        self,
        weather: dict,
    ) -> str:
        """
        Transforme les données météo en une phrase simple,
        exploitable comme contexte dans le prompt Gemini.
        """

        parts = [
            f"Météo actuelle : {weather['description']}, "
            f"{weather['temperature_c']}°C, "
            f"humidité {weather['humidity_percent']}%, "
            f"vent {weather['wind_speed_kmh']} km/h."
        ]

        if (
            weather.get(
                "rain_probability_today_percent"
            )
            is not None
        ):

            parts.append(
                "Probabilité de pluie aujourd'hui : "
                f"{weather['rain_probability_today_percent']}%, "
                "cumul attendu : "
                f"{weather.get('rain_total_today_mm', 0)} mm."
            )

        return " ".join(parts)
import requests as http_requests

from django.conf import settings
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import WeatherRecord
from .serializers import WeatherRecordSerializer

# ── Existing CRUD viewset (kept for compatibility) ─────────────────────────

class WeatherRecordViewSet(viewsets.ModelViewSet):
    """Weather records — readable and writable by all authenticated users."""
    queryset = WeatherRecord.objects.all()
    serializer_class = WeatherRecordSerializer
    permission_classes = [IsAuthenticated]


# ── Live weather from OpenWeatherMap ──────────────────────────────────────

OWM_URL = 'https://api.openweathermap.org/data/2.5/weather'

WIND_DIR = [
    'N','NNE','NE','ENE','E','ESE','SE','SSE',
    'S','SSW','SW','WSW','W','WNW','NW','NNW',
]

def _wind_direction(degrees: float) -> str:
    idx = round(degrees / 22.5) % 16
    return WIND_DIR[idx]


def _clean_location(raw: str) -> str:
    """
    Profile location format: "Province, City, Country"
    We always want the City (index 1 in comma-split).

    Examples:
        "Punjab, Lahore, Pakistan"  → "Lahore"
        "Sindh, Karachi, Pakistan"  → "Karachi"
        "Lahore, Pakistan"          → "Lahore"   (index 0)
        "Lahore"                    → "Lahore"
    """
    parts = [p.strip() for p in raw.split(',') if p.strip()]
    if len(parts) >= 3:
        return parts[1]   # Province, **City**, Country
    if len(parts) == 2:
        return parts[0]   # **City**, Country
    return parts[0] if parts else raw

def _advisory(data: dict) -> str:
    """Return a short farming advisory based on weather conditions."""
    temp   = data.get('temp', 0)
    humid  = data.get('humidity', 0)
    wind   = data.get('wind_speed', 0)
    desc   = data.get('description', '').lower()
    rain   = data.get('rain_1h', 0)

    lines = []

    if rain > 5:
        lines.append('Heavy rain expected — avoid spraying pesticides today.')
    elif rain > 0:
        lines.append('Light rain — hold off on irrigation.')
    elif temp > 38:
        lines.append('Extreme heat — water crops early morning or after sunset.')
    elif temp > 32:
        lines.append('Hot day — ensure adequate soil moisture.')
    elif temp < 5:
        lines.append('Cold weather — protect sensitive crops from frost.')

    if humid > 80 and temp > 20:
        lines.append('High humidity — watch for fungal disease.')
    if wind > 10:
        lines.append('Strong winds — secure any covers or structures.')
    if 'storm' in desc or 'thunder' in desc:
        lines.append('Storm conditions — stay indoors, delay field work.')

    return ' '.join(lines) if lines else 'Conditions look good for regular farm work today.'


class WeatherLiveView(APIView):
    """
    GET /api/weather/live/
    Auto-uses the authenticated user's profile.location.
    Also accepts ?location=<city> to override.

    Returns current weather from OpenWeatherMap.
    No database writes — purely live data.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        api_key = settings.OPENWEATHER_API_KEY
        if not api_key:
            return Response(
                {'detail': 'Weather service is not configured.'},
                status=503,
            )

        # Resolve location: query param > user profile > fallback
        location = request.query_params.get('location', '').strip()
        if not location:
            try:
                location = request.user.profile.location.strip()
            except Exception:
                location = ''
        if not location:
            return Response(
                {'detail': 'No location found. Please set your location in your profile.'},
                status=400,
            )

        # OpenWeatherMap only accepts plain city names.
        # Strip common separators and take the most specific part.
        # e.g. "Punjab, Lahore, Pakistan" → "Lahore"
        #      "Lahore"                   → "Lahore"
        #      "Lahore Pakistan"          → "Lahore"
        location = _clean_location(location)

        try:
            resp = http_requests.get(
                OWM_URL,
                params={
                    'q': location,
                    'appid': api_key,
                    'units': 'metric',
                },
                timeout=10,
            )
            if resp.status_code == 404:
                return Response(
                    {'detail': f'Location "{location}" not found. Try a different city name.'},
                    status=404,
                )
            resp.raise_for_status()
        except http_requests.RequestException as exc:
            return Response(
                {'detail': f'Weather service unavailable: {exc}'},
                status=503,
            )

        raw = resp.json()
        main    = raw.get('main', {})
        wind    = raw.get('wind', {})
        weather = raw.get('weather', [{}])[0]
        rain    = raw.get('rain', {})
        sys     = raw.get('sys', {})

        data = {
            'location':       raw.get('name', location),
            'country':        sys.get('country', ''),
            'temp':           round(main.get('temp', 0), 1),
            'feels_like':     round(main.get('feels_like', 0), 1),
            'temp_min':       round(main.get('temp_min', 0), 1),
            'temp_max':       round(main.get('temp_max', 0), 1),
            'humidity':       main.get('humidity', 0),
            'pressure':       main.get('pressure', 0),
            'description':    weather.get('description', '').capitalize(),
            'icon':           weather.get('icon', ''),
            'icon_url':       f"https://openweathermap.org/img/wn/{weather.get('icon','01d')}@2x.png",
            'wind_speed':     round(wind.get('speed', 0), 1),
            'wind_direction': _wind_direction(wind.get('deg', 0)),
            'visibility':     raw.get('visibility', 0),
            'cloudiness':     raw.get('clouds', {}).get('all', 0),
            'rain_1h':        rain.get('1h', 0),
            'sunrise':        sys.get('sunrise', 0),
            'sunset':         sys.get('sunset', 0),
        }

        data['advisory'] = _advisory(data)

        return Response(data)

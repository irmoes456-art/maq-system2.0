import React, { useEffect, useRef, useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { GoogleMap, useJsApiLoader } from '@react-google-maps/api';
import { Loader2, MapPin, Clock, Bike, AlertTriangle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || '';
const API = `${BACKEND_URL}/api`;
const GOOGLE_MAPS_KEY = process.env.REACT_APP_GOOGLE_MAPS_API_KEY || '';
const GOOGLE_MAPS_LIBRARIES = ['places', 'geometry'];

const MOTO_SVG_BASE = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 56 56" width="56" height="56"><circle cx="28" cy="28" r="26" fill="#1a73e8" stroke="#fff" stroke-width="3"/><circle cx="28" cy="28" r="22" fill="#1a1a2e" stroke="#4285F4" stroke-width="2"/><g transform="translate(28,28) rotate(__HEADING__)"><path d="M-5,-14 L0,-18 L5,-14 L3,-3 L5,10 L1.5,15 L-1.5,15 L-5,10 L-3,-3 Z" fill="#4285F4"/><circle cx="0" cy="-16" r="3" fill="#60a5fa"/><path d="M-8,-5 L-11,-1 L-8,0 Z" fill="#60a5fa" opacity="0.8"/><path d="M8,-5 L11,-1 L8,0 Z" fill="#60a5fa" opacity="0.8"/></g></svg>`;

const haversine = (lat1, lng1, lat2, lng2) => {
  const R = 6371e3;
  const φ1 = lat1 * Math.PI / 180;
  const φ2 = lat2 * Math.PI / 180;
  const Δφ = (lat2 - lat1) * Math.PI / 180;
  const Δλ = (lng2 - lng1) * Math.PI / 180;
  const a = Math.sin(Δφ / 2) ** 2 + Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
};

export default function PublicTrackingPage() {
  const { token } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const mapRef = useRef(null);
  const techMarkerRef = useRef(null);
  const customerMarkerRef = useRef(null);
  const polylineRef = useRef(null);

  const { isLoaded } = useJsApiLoader({
    googleMapsApiKey: GOOGLE_MAPS_KEY,
    libraries: GOOGLE_MAPS_LIBRARIES,
  });

  const fetchData = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/tracking/public/${token}`);
      setData(res.data);
      setLastUpdated(new Date());
      setError(null);
    } catch (e) {
      const status = e?.response?.status;
      if (status === 410) setError('Este link expirou.');
      else if (status === 401) setError('Link inválido.');
      else if (status === 404) setError('OS não encontrada.');
      else setError('Não foi possível carregar a localização.');
    }
  }, [token]);

  useEffect(() => {
    fetchData();
    const i = setInterval(fetchData, 5000);
    return () => clearInterval(i);
  }, [fetchData]);

  const onMapLoad = useCallback((map) => {
    mapRef.current = map;
  }, []);

  // Update markers & route when data changes
  useEffect(() => {
    if (!isLoaded || !mapRef.current || !data) return;
    const map = mapRef.current;
    const google = window.google;

    // Customer marker
    const osLat = data.os?.lat;
    const osLng = data.os?.lng;
    if (osLat && osLng) {
      if (!customerMarkerRef.current) {
        customerMarkerRef.current = new google.maps.Marker({
          position: { lat: osLat, lng: osLng },
          map,
          title: data.os.customer_name,
          icon: {
            path: google.maps.SymbolPath.CIRCLE,
            scale: 10,
            fillColor: '#ef4444',
            fillOpacity: 1,
            strokeColor: '#fff',
            strokeWeight: 3,
          },
        });
      }
    }

    // Technician marker
    const live = data.live;
    if (live?.lat && live?.lng) {
      const svg = MOTO_SVG_BASE.replace('__HEADING__', String(live.heading || 0));
      const icon = {
        url: `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`,
        scaledSize: new google.maps.Size(56, 56),
        anchor: new google.maps.Point(28, 28),
      };
      if (!techMarkerRef.current) {
        techMarkerRef.current = new google.maps.Marker({
          position: { lat: live.lat, lng: live.lng },
          map,
          icon,
          zIndex: 200,
        });
        if (osLat && osLng) {
          const bounds = new google.maps.LatLngBounds();
          bounds.extend({ lat: live.lat, lng: live.lng });
          bounds.extend({ lat: osLat, lng: osLng });
          map.fitBounds(bounds, { top: 60, bottom: 80, left: 40, right: 40 });
        } else {
          map.setCenter({ lat: live.lat, lng: live.lng });
          map.setZoom(15);
        }
      } else {
        techMarkerRef.current.setPosition({ lat: live.lat, lng: live.lng });
        techMarkerRef.current.setIcon(icon);
      }

      // Road-following polyline (sent by the technician's DirectionsService
      // result). Falls back to a straight tech→customer line only if nav
      // path hasn't been published yet.
      const trafficKey = live.nav_traffic_color || 'normal';
      const colorMap = { lightblue: '#1ec3ff', normal: '#4285F4', yellow: '#f59e0b', red: '#dc2626' };
      const lineColor = colorMap[trafficKey] || '#4285F4';
      const navPath = (live.nav_path && Array.isArray(live.nav_path) && live.nav_path.length > 1)
        ? live.nav_path
        : (osLat && osLng ? [{ lat: live.lat, lng: live.lng }, { lat: osLat, lng: osLng }] : null);
      if (navPath) {
        if (!polylineRef.current) {
          polylineRef.current = new google.maps.Polyline({
            map, path: navPath,
            strokeColor: lineColor,
            strokeOpacity: 0.9,
            strokeWeight: 6,
          });
          // Glow underlayer for "GPS look"
          new google.maps.Polyline({
            map, path: navPath,
            strokeColor: lineColor,
            strokeOpacity: 0.25,
            strokeWeight: 14,
            zIndex: 0,
          });
        } else {
          polylineRef.current.setPath(navPath);
          polylineRef.current.setOptions({ strokeColor: lineColor });
        }
      }
    }
  }, [data, isLoaded]);

  // ETA: prefer real Directions ETA (duration_in_traffic), fallback haversine
  const eta = (() => {
    if (data?.live?.nav_duration_in_traffic_seconds || data?.live?.nav_duration_seconds) {
      const secs = data.live.nav_duration_in_traffic_seconds || data.live.nav_duration_seconds;
      const mins = Math.max(1, Math.round(secs / 60));
      const km = data.live.nav_distance_meters ? (data.live.nav_distance_meters / 1000).toFixed(1) : '—';
      return { distKm: km, minutes: mins };
    }
    if (!data?.live?.lat || !data?.os?.lat) return null;
    const dist = haversine(data.live.lat, data.live.lng, data.os.lat, data.os.lng);
    const speed = Math.max(data.live.speed || 25, 8);
    const minutes = Math.round((dist / 1000) / (speed) * 60);
    return { distKm: (dist / 1000).toFixed(1), minutes };
  })();

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <div className="bg-white rounded-xl shadow-lg p-8 max-w-md text-center" data-testid="public-tracking-error">
          <AlertTriangle className="h-12 w-12 text-amber-500 mx-auto mb-3" />
          <h1 className="text-lg font-semibold text-gray-900">{error}</h1>
          <p className="text-sm text-gray-500 mt-2">Solicite um novo link à Mastermaq.</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col" data-testid="public-tracking-page">
      {/* Header */}
      <header className="bg-white shadow-sm border-b px-4 py-3 flex items-center justify-between">
        <div>
          <h1 className="text-sm sm:text-base font-semibold text-gray-900">Mastermaq Assistência Técnica</h1>
          <p className="text-[11px] text-gray-500">Acompanhamento em tempo real</p>
        </div>
        <div className="text-right">
          <p className="text-[11px] text-gray-500">OS Nº</p>
          <p className="text-sm font-bold text-gray-900">{data.os?.os_number}</p>
        </div>
      </header>

      {/* Map */}
      <div className="flex-1 relative" style={{ minHeight: '50vh' }}>
        {isLoaded ? (
          <GoogleMap
            mapContainerStyle={{ width: '100%', height: '100%', minHeight: '50vh' }}
            zoom={13}
            center={{ lat: data.live?.lat || data.os?.lat || -19.9167, lng: data.live?.lng || data.os?.lng || -43.9345 }}
            onLoad={onMapLoad}
            options={{
              disableDefaultUI: true,
              zoomControl: true,
              gestureHandling: 'greedy',
            }}
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
            <div className="text-center">
              <Loader2 className="h-6 w-6 animate-spin text-gray-400 mx-auto" />
              <p className="text-xs text-gray-500 mt-2">Carregando mapa…</p>
            </div>
          </div>
        )}

        {/* Status pill (when no live data) */}
        {!data.live && (
          <div className="absolute top-3 left-1/2 -translate-x-1/2 bg-amber-100 text-amber-800 px-3 py-1.5 rounded-full text-xs shadow flex items-center gap-2" data-testid="public-no-live">
            <Clock className="h-3 w-3" /> Aguardando o início da navegação do técnico…
          </div>
        )}
      </div>

      {/* Bottom info card */}
      <div className="bg-white border-t shadow-lg p-4 space-y-3" data-testid="public-info-card">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
            <Bike className="h-5 w-5 text-blue-700" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs text-gray-500">Técnico</p>
            <p className="text-sm font-semibold text-gray-900 truncate">{data.technician_name || 'Atendimento'}</p>
          </div>
          {eta && (
            <div className="text-right">
              <p className="text-[10px] text-gray-500">ETA</p>
              <p className="text-sm font-bold text-blue-700" data-testid="public-eta">{eta.minutes} min</p>
              <p className="text-[10px] text-gray-400">{eta.distKm} km</p>
            </div>
          )}
        </div>

        <div className="flex items-start gap-2 text-xs">
          <MapPin className="h-4 w-4 text-gray-400 shrink-0 mt-0.5" />
          <div className="min-w-0">
            <p className="text-gray-700 truncate">{data.os?.customer_name}</p>
            <p className="text-gray-500 truncate">{data.os?.address}{data.os?.neighborhood ? ` — ${data.os.neighborhood}` : ''}{data.os?.city ? `, ${data.os.city}` : ''}</p>
          </div>
        </div>

        {lastUpdated && (
          <p className="text-[10px] text-gray-400 text-center" data-testid="public-last-update">
            Atualizado às {lastUpdated.toLocaleTimeString('pt-BR')}
          </p>
        )}
      </div>
    </div>
  );
}

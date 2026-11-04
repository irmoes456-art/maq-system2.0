import React, { useEffect, useRef, useState, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { GoogleMap, useJsApiLoader } from '@react-google-maps/api';
import { Loader2, AlertTriangle } from 'lucide-react';
import '../rotaflow.css';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;
const GOOGLE_MAPS_LIBRARIES = ['places', 'geometry'];
const MAP_OPTIONS = {
  disableDefaultUI: true,
  gestureHandling: 'greedy',
  mapId: process.env.REACT_APP_GOOGLE_MAP_ID || 'DEMO_MAP_ID',
  renderingType: 'VECTOR',
  clickableIcons: false,
  keyboardShortcuts: false,
};
const MAP_STYLE = { width: '100%', height: '100%' };
const BH = { lat: -19.9167, lng: -43.9345 };

const MOTO_SVG_BASE = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 56 56" width="56" height="56"><circle cx="28" cy="28" r="26" fill="#1a73e8" stroke="#fff" stroke-width="3"/><circle cx="28" cy="28" r="22" fill="#1a1a2e" stroke="#4285F4" stroke-width="2"/><g transform="translate(28,28) rotate(__HEADING__)"><path d="M-5,-14 L0,-18 L5,-14 L3,-3 L5,10 L1.5,15 L-1.5,15 L-5,10 L-3,-3 Z" fill="#4285F4"/><circle cx="0" cy="-16" r="3" fill="#60a5fa"/></g></svg>`;

// Link do consumidor: somente o mapa com a rota do técnico até a OS, sem badges/botões/pop-ups.
export default function PublicTrackingPage() {
  const { token } = useParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const mapRef = useRef(null);
  const techMarkerRef = useRef(null);
  const customerMarkerRef = useRef(null);
  const polylineRef = useRef(null);
  const outlineRef = useRef(null);
  const fitted = useRef(false);

  const { isLoaded } = useJsApiLoader({
    googleMapsApiKey: process.env.REACT_APP_GOOGLE_MAPS_API_KEY,
    libraries: GOOGLE_MAPS_LIBRARIES,
  });

  const fetchData = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/tracking/public/${token}`);
      setData(res.data);
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
    const i = setInterval(fetchData, 3000);
    return () => clearInterval(i);
  }, [fetchData]);

  const onMapLoad = useCallback((map) => { mapRef.current = map; }, []);

  useEffect(() => {
    if (!isLoaded || !mapRef.current || !data) return;
    const map = mapRef.current;
    const google = window.google;
    const dest = data.os?.lat && data.os?.lng ? { lat: data.os.lat, lng: data.os.lng } : null;
    if (dest && !customerMarkerRef.current) {
      customerMarkerRef.current = new google.maps.Marker({
        position: dest, map, clickable: false,
        icon: { path: google.maps.SymbolPath.CIRCLE, scale: 10, fillColor: '#1d4ed8', fillOpacity: 1, strokeColor: '#fff', strokeWeight: 3 },
      });
    }
    const live = data.live;
    if (!live?.lat || !live?.lng) {
      if (dest && !fitted.current) { map.setCenter(dest); map.setZoom(15); }
      return;
    }
    const pos = { lat: live.lat, lng: live.lng };
    const icon = {
      url: `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(MOTO_SVG_BASE.replace('__HEADING__', String(live.heading || 0)))}`,
      scaledSize: new google.maps.Size(56, 56),
      anchor: new google.maps.Point(28, 28),
    };
    if (!techMarkerRef.current) {
      techMarkerRef.current = new google.maps.Marker({ position: pos, map, icon, zIndex: 200, clickable: false });
    } else {
      techMarkerRef.current.setPosition(pos);
      techMarkerRef.current.setIcon(icon);
    }
    const sameOs = !live.active_os || String(live.active_os) === String(data.os?.os_number);
    const path = sameOs && live.nav_path?.length > 1 ? live.nav_path : (dest ? [pos, dest] : null);
    if (path) {
      if (!polylineRef.current) {
        outlineRef.current = new google.maps.Polyline({ map, path, strokeColor: '#1E3A8A', strokeWeight: 11, zIndex: 2, clickable: false });
        polylineRef.current = new google.maps.Polyline({ map, path, strokeColor: '#3B82F6', strokeWeight: 7, zIndex: 3, clickable: false });
      } else {
        polylineRef.current.setPath(path);
        outlineRef.current.setPath(path);
      }
    }
    if (!fitted.current && dest) {
      fitted.current = true;
      const b = new google.maps.LatLngBounds();
      (path || [pos, dest]).forEach((p) => b.extend(p));
      map.fitBounds(b, 50);
    }
  }, [data, isLoaded]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <div className="bg-white rounded-xl shadow-lg p-8 max-w-md text-center" data-testid="public-tracking-error">
          <AlertTriangle className="h-12 w-12 text-amber-500 mx-auto mb-3" />
          <h1 className="text-lg font-semibold text-gray-900">{error}</h1>
        </div>
      </div>
    );
  }

  if (!data || !isLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    );
  }

  return (
    <div className="rf-root rf-light h-[100dvh] w-screen" data-testid="public-tracking-page">
      <GoogleMap
        mapContainerStyle={MAP_STYLE}
        zoom={13}
        center={BH}
        onLoad={onMapLoad}
        options={MAP_OPTIONS}
      />
    </div>
  );
}

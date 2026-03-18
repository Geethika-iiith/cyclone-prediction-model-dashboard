import React, { useState, useEffect } from 'react';
import { 
  CloudRain, Wind, AlertTriangle, ShieldCheck, 
  Map as MapIcon, BarChart2, Zap, Activity
} from 'lucide-react';
import { 
  BarChart, Bar, AreaChart, Area, XAxis, YAxis, 
  CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer 
} from 'recharts';
import { MapContainer, TileLayer, Marker, Popup, Circle, Polyline, FeatureGroup } from 'react-leaflet';
import L from 'leaflet';
import './index.css';

// Fix Leaflet icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const customIcons = {
  city: new L.DivIcon({
    className: 'custom-icon',
    html: `<div style="background-color: #3b82f6; width: 14px; height: 14px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 10px rgba(59, 130, 246, 0.8);"></div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10]
  }),
  cyclone: new L.DivIcon({
    className: 'custom-icon',
    html: `<div style="background-color: #ef4444; width: 20px; height: 20px; border-radius: 50%; border: 4px solid rgba(239, 68, 68, 0.4); box-shadow: 0 0 15px rgba(239, 68, 68, 1); animation: pulse 2s infinite;"></div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14]
  }),
  shelter: new L.DivIcon({
    className: 'custom-icon',
    html: `<div style="background-color: #10b981; width: 12px; height: 12px; border-radius: 3px; border: 2px solid white; box-shadow: 0 0 8px rgba(16, 185, 129, 0.8);"></div>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8]
  })
};

function App() {
  const [cities, setCities] = useState([]);
  const [selectedCity, setSelectedCity] = useState('');
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch('http://localhost:8000/api/cities')
      .then(res => res.json())
      .then(data => {
        setCities(data.cities);
      })
      .catch(err => console.error("Error fetching cities:", err));
  }, []);

  const handleCityChange = (e) => {
    const cityName = e.target.value;
    setSelectedCity(cityName);
    
    if (!cityName) {
      setDashboardData(null);
      return;
    }

    const cityObj = cities.find(c => c.city === cityName);
    if (!cityObj) return;

    setLoading(true);
    fetch(`http://localhost:8000/api/predict?city=${encodeURIComponent(cityName)}&lat=${cityObj.latitude}&lon=${cityObj.longitude}&pop_density=${cityObj.population_density}&sim=true`)
      .then(res => res.json())
      .then(data => {
        setDashboardData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching predictions:", err);
        setLoading(false);
      });
  };

  if (loading) {
    return (
      <div className="app-container">
        <header className="dashboard-header">
          <div className="logo-container">
            <Zap className="logo-icon" size={32} color="#3b82f6" />
            <div className="logo-text">
              <h1>Cyclone<span>Guard</span></h1>
              <p>Predictive Safety Intelligence</p>
            </div>
          </div>
        </header>
        <div className="loader-container">
          <div className="spinner"></div>
          <h2>Acquiring Meteorological Data...</h2>
          <p>Analyzing predictive models and satellite telemetry</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app-container">
      <header className="dashboard-header">
        <div className="logo-container">
          <Zap className="logo-icon" size={32} color="#3b82f6" />
          <div className="logo-text">
            <h1>Cyclone<span>Guard</span></h1>
            <p>Predictive Safety Intelligence</p>
          </div>
        </div>
        
        <div className="controls-container">
          {dashboardData && (
            <div style={{ marginRight: '1rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end'}}>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)'}}>Live Weather</span>
                <span style={{ fontWeight: '600'}}>{dashboardData.weather?.current_weather?.temperature}°C | {dashboardData.weather?.current_weather?.windspeed} km/h</span>
              </div>
              <Activity color="#10b981" size={24} />
            </div>
          )}
          <select value={selectedCity} onChange={handleCityChange}>
            <option value="">-- Select Region --</option>
            {cities.map((city, idx) => (
              <option key={idx} value={city.city}>{city.city}</option>
            ))}
          </select>
        </div>
      </header>

      {!selectedCity || !dashboardData ? (
        <main className="welcome-screen">
          <h2>Next-Generation Cyclone Intelligence</h2>
          <p>Protecting coastal communities through real-time ML-powered predictions. 
          Select a region from the top right to initialize the assessment protocol and view dynamic risk mapping.</p>
        </main>
      ) : (
        <main className="dashboard-grid">
          
          {/* Key Metrics */}
          <div className="card-metrics">
            {/* Disaster Risk */}
            <div className={`metric-card`} data-risk={dashboardData.predictions?.risk?.risk_level}>
              <div className="metric-header">
                <div className="metric-icon"><ShieldCheck size={20} color="var(--text-primary)" /></div>
                <span>Cyclone Risk Level</span>
              </div>
              <div>
                <div className="metric-value">
                  <span className={`risk-badge risk-${dashboardData.predictions?.risk?.risk_level}`}>
                    {dashboardData.predictions?.risk?.risk_level?.toUpperCase()}
                  </span>
                </div>
                <div className="metric-sub">Confidence: {(dashboardData.predictions?.risk?.confidence * 100).toFixed(1)}%</div>
              </div>
            </div>

            {/* Cyclonic Proximity */}
            <div className="metric-card">
               <div className="metric-header">
                <div className="metric-icon"><AlertTriangle size={20} color="#8b5cf6" /></div>
                <span>Cyclone Proximity</span>
              </div>
              <div>
                <div className="metric-value" style={{ color: '#8b5cf6' }}>
                  {Math.round(dashboardData.cyclone?.distance_km || 0)} km
                </div>
                <div className="metric-sub">
                  Closest Approach (24h): {Math.round(dashboardData.predictions?.cyclone_path?.closest_approach_km || 0)} km
                </div>
              </div>
            </div>

            {/* Max Wind Speed */}
            <div className="metric-card">
              <div className="metric-header">
                <div className="metric-icon"><Wind size={20} color="#f97316" /></div>
                <span>Predicted Wind Impact</span>
              </div>
              <div>
                <div className="metric-value" style={{ color: '#f97316' }}>
                  {Math.round(dashboardData.predictions?.wind?.predicted_wind_kmh || 0)} km/h
                </div>
                <div className="metric-sub">Model derived expected peak speed</div>
              </div>
            </div>

            {/* Total Rainfall */}
            <div className="metric-card">
              <div className="metric-header">
                <div className="metric-icon"><CloudRain size={20} color="#3b82f6" /></div>
                <span>Projected Rainfall</span>
              </div>
              <div>
                <div className="metric-value" style={{ color: '#3b82f6' }}>
                  {dashboardData.predictions?.rainfall?.predictions?.length 
                    ? Math.max(...dashboardData.predictions.rainfall.predictions.map(p => p.predicted_rainfall_mm)).toFixed(1)
                    : 0} mm
                </div>
                <div className="metric-sub">Maximum observed daily prediction</div>
              </div>
            </div>
          </div>

          {/* Interactive Map */}
          <div className="map-container">
            <h3 className="section-title"><MapIcon size={20} /> Tactical Operations Map</h3>
            <div style={{ flex: 1, borderRadius: 'var(--radius-md)', overflow: 'hidden' }}>
              <MapContainer 
                center={[dashboardData.cyclone?.lat || 20, dashboardData.cyclone?.lon || 80]} 
                zoom={5} 
                style={{ height: '100%', width: '100%' }}
                zoomControl={false}
              >
                <TileLayer
                  url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                  attribution='&copy; <a href="https://carto.com/">CartoDB</a>'
                />
                
                {/* City Marker */}
                {cities.find(c => c.city === selectedCity) && (
                  <Marker 
                    position={[
                      cities.find(c => c.city === selectedCity).latitude, 
                      cities.find(c => c.city === selectedCity).longitude
                    ]}
                    icon={customIcons.city}
                  >
                    <Popup>
                      <strong>{selectedCity}</strong><br/>Population Center
                    </Popup>
                  </Marker>
                )}

                {/* Cyclone Data */}
                {dashboardData.cyclone && (
                  <>
                    <Marker 
                      position={[dashboardData.cyclone.lat, dashboardData.cyclone.lon]}
                      icon={customIcons.cyclone}
                    >
                      <Popup>
                        <strong>{dashboardData.cyclone.name}</strong><br/>
                        Category: {dashboardData.cyclone.category}<br/>
                        Wind: {dashboardData.cyclone.wind_kmh} km/h
                      </Popup>
                    </Marker>
                    
                    {/* Danger Zones */}
                    <Circle 
                      center={[dashboardData.cyclone.lat, dashboardData.cyclone.lon]} 
                      radius={150000} 
                      pathOptions={{ color: '#ef4444', fillColor: '#ef4444', fillOpacity: 0.15, weight: 1 }} 
                    />
                    <Circle 
                      center={[dashboardData.cyclone.lat, dashboardData.cyclone.lon]} 
                      radius={300000} 
                      pathOptions={{ color: '#f97316', fillColor: '#f97316', fillOpacity: 0.08, weight: 1, dashArray: '5, 5' }} 
                    />

                    {/* Tracks */}
                    {dashboardData.cyclone.track?.length > 0 && (
                      <Polyline 
                         positions={dashboardData.cyclone.track.map(t => [t.lat, t.lon])}
                         pathOptions={{ color: '#ef4444', weight: 3, opacity: 0.6 }}
                      />
                    )}
                    {dashboardData.predictions?.cyclone_path?.predicted_positions?.length > 0 && (
                      <Polyline 
                         positions={[
                           [dashboardData.cyclone.lat, dashboardData.cyclone.lon],
                           ...dashboardData.predictions.cyclone_path.predicted_positions.map(t => [t.lat, t.lon])
                         ]}
                         pathOptions={{ color: '#eab308', weight: 3, opacity: 0.8, dashArray: '8, 8' }}
                      />
                    )}
                  </>
                )}

                {/* Shelters */}
                {dashboardData.shelters && dashboardData.shelters.length > 0 && (
                  <FeatureGroup>
                    {dashboardData.shelters.map((s, idx) => (
                      <Marker key={idx} position={[s.lat, s.lon]} icon={customIcons.shelter}>
                         <Popup>{s.name || "Evacuation Center"}</Popup>
                      </Marker>
                    ))}
                  </FeatureGroup>
                )}
              </MapContainer>
            </div>
          </div>

          {/* Charts Area */}
          <div className="charts-container">
            <div className="chart-card">
              <h3 className="section-title" style={{ fontSize: '1rem' }}><CloudRain size={16} /> Projected Precipitation (mm)</h3>
              <div style={{ width: '100%', height: 'calc(100% - 2.5rem)' }}>
                <ResponsiveContainer>
                  <BarChart 
                    data={dashboardData.weather?.daily?.time?.map((t, idx) => ({
                      date: new Date(t).toLocaleDateString(undefined, {weekday: 'short'}),
                      actual: dashboardData.weather.daily.rain_sum?.[idx] || 0,
                      predicted: dashboardData.predictions?.rainfall?.predictions?.[idx]?.predicted_rainfall_mm || 0
                    })).slice(0, 7) || []}
                    margin={{ top: 5, right: 0, left: -20, bottom: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                    <XAxis dataKey="date" stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
                    <RechartsTooltip cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
                    <Bar dataKey="predicted" name="Model Prediction" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={20} />
                    <Bar dataKey="actual" name="Forecast" fill="#8b5cf6" radius={[4, 4, 0, 0]} barSize={20} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="chart-card">
               <h3 className="section-title" style={{ fontSize: '1rem' }}><Wind size={16} /> Wind Velocity Trend (km/h)</h3>
               <div style={{ width: '100%', height: 'calc(100% - 2.5rem)' }}>
                <ResponsiveContainer>
                  <AreaChart 
                    data={dashboardData.weather?.daily?.time?.map((t, idx) => ({
                      date: new Date(t).toLocaleDateString(undefined, {weekday: 'short'}),
                      maxWind: dashboardData.weather.daily.windspeed_10m_max?.[idx] || 0,
                      gust: dashboardData.weather.daily.windgusts_10m_max?.[idx] || 0
                    })).slice(0, 7) || []}
                    margin={{ top: 5, right: 0, left: -20, bottom: 0 }}
                  >
                    <defs>
                      <linearGradient id="colorWind" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#f97316" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#f97316" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                    <XAxis dataKey="date" stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
                    <RechartsTooltip />
                    <Area type="monotone" dataKey="maxWind" name="Max Wind" stroke="#f97316" fillOpacity={1} fill="url(#colorWind)" strokeWidth={2} />
                    <Area type="monotone" dataKey="gust" name="Gusts" stroke="#ef4444" fill="none" strokeWidth={2} strokeDasharray="5 5" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

        </main>
      )}
    </div>
  );
}

export default App;

Title: Air Quality Dashboard
Date: 2026-06-04
Slug: aqi
Summary: Live air quality index for Nepali cities — Kathmandu, Pokhara, Bharatpur.

# Air Quality Dashboard

<div id="aqi-dashboard" style="max-width: 900px; margin: 2rem auto;">
  <div id="aqi-loading">Loading air quality data...</div>
  <div id="aqi-cards" style="display:none; display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:1.5rem;"></div>
  <p style="font-size:0.8rem; color:#6b7280; margin-top:1rem;">Data source: IQAir. Updates hourly. API key stored server-side.</p>
</div>

<script>
(function() {
  const CITIES = [
    { name: "Kathmandu", lat: 27.7172, lon: 85.3240 },
    { name: "Pokhara", lat: 28.2096, lon: 83.9856 },
    { name: "Bharatpur", lat: 27.6833, lon: 84.4333 },
  ];

  const AQI_COLORS = [
    { max: 50, color: "#00e400", label: "Good" },
    { max: 100, color: "#ffff00", label: "Moderate" },
    { max: 150, color: "#ff7e00", label: "Unhealthy for Sensitive" },
    { max: 200, color: "#ff0000", label: "Unhealthy" },
    { max: 300, color: "#8f3f97", label: "Very Unhealthy" },
    { max: Infinity, color: "#7e0023", label: "Hazardous" },
  ];

  function getAqiInfo(aqi) {
    for (let i = 0; i < AQI_COLORS.length; i++) {
      if (aqi <= AQI_COLORS[i].max) return AQI_COLORS[i];
    }
    return AQI_COLORS[AQI_COLORS.length - 1];
  }

  function renderCard(city, aqi) {
    if (aqi === null) {
      return `<div class="aqi-card" style="background:#f3f4f6;border-radius:8px;padding:1.5rem;text-align:center;">
        <h3>${city.name}</h3>
        <p style="color:#6b7280;">Data unavailable</p>
      </div>`;
    }
    const info = getAqiInfo(aqi);
    return `<div class="aqi-card" style="background:${info.color}22;border-left:4px solid ${info.color};border-radius:8px;padding:1.5rem;">
      <h3 style="margin:0 0 0.75rem;">${city.name}</h3>
      <div style="font-size:3rem;font-weight:700;color:${info.color};">${aqi}</div>
      <p style="font-weight:600;color:${info.color};">${info.label}</p>
      <p style="font-size:0.8rem;color:#6b7280;">AQI (US)</p>
    </div>`;
  }

  async function fetchAqi() {
    const container = document.getElementById("aqi-cards");
    const loading = document.getElementById("aqi-loading");
    try {
      const res = await fetch("/api/aqi");
      const data = res.ok ? await res.json() : null;
      let html = "";
      for (const city of CITIES) {
        const val = data ? data[city.name] || null : null;
        html += renderCard(city, val);
      }
      container.innerHTML = html;
    } catch (e) {
      container.innerHTML = CITIES.map(c => renderCard(c, null)).join("");
    }
    loading.style.display = "none";
    container.style.display = "grid";
  }

  fetchAqi();
  setInterval(fetchAqi, 3600000);
})();
</script>

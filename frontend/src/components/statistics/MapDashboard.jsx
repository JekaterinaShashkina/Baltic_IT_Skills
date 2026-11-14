import { useEffect, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

import { API_BASE_URL } from "../../config/const";

export const MapDashboard = () => {
  const [locations, setLocations] = useState([]);
  const [country, setCountry] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const controller = new AbortController();

    const loadLocations = async () => {
      setLoading(true);
      setError(null);

      try {
        const url =
          country === "all"
            ? `${API_BASE_URL}/jobs/map`
            : `${API_BASE_URL}/jobs/map?country=${country}`;

        const response = await fetch(url, {
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error("Failed to load job locations");
        }

        const data = await response.json();
        setLocations(data);
      } catch (err) {
        if (err.name !== "AbortError") {
          setError(err.message);
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    };

    loadLocations();

    return () => controller.abort();
  }, [country]);

  if (loading && locations.length === 0) {
    return <p>Loading job locations...</p>;
  }

  if (error && locations.length === 0) {
    return <p>{error}</p>;
  }

  return (
    <section className="map-dashboard">
      <h2>Job Locations</h2>
      <p>
        Geographic distribution of job locations mentioned in MeetFrank
        vacancies collected for the Baltic countries.
      </p>

      <div className="map-filters">
        {[
          { value: "all", label: "All" },
          { value: "estonia", label: "Estonia" },
          { value: "latvia", label: "Latvia" },
          { value: "lithuania", label: "Lithuania" },
        ].map((option) => (
          <button
            key={option.value}
            type="button"
            className={`map-filter-button ${
              country === option.value ? "active" : ""
            }`}
            onClick={() => setCountry(option.value)}
          >
            {option.label}
          </button>
        ))}
      </div>

      <MapContainer
        center={[53, 18]}
        zoom={4}
        scrollWheelZoom={false}
        style={{
          height: "550px",
          width: "100%",
          borderRadius: "12px",
        }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {locations.map((location) => (
          <CircleMarker
            key={location.city}
            center={[location.latitude, location.longitude]}
            radius={Math.max(
              5,
              Math.min(22, 5 + Math.sqrt(location.jobCount) * 1.5),
            )}
            pathOptions={{
              color: "#38b2ac",
              fillColor: "#38b2ac",
              fillOpacity: 0.65,
              weight: 1,
            }}
          >
            <Popup>
              <strong>
                {location.city}, {location.country}
              </strong>
              <div>
                {location.jobCount} {location.jobCount === 1 ? "job" : "jobs"}
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
      <p className="map-note">
        Locations are based on cities mentioned in MeetFrank job postings. A
        single posting may reference multiple cities, so city counts may exceed
        the total number of unique jobs. Country filters refer to the MeetFrank
        data collection country, not the geographic location of the city.
      </p>
    </section>
  );
};

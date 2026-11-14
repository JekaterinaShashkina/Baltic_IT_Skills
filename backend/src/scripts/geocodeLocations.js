const Database = require("better-sqlite3");
const path = require("path");

const dbPath = path.join(__dirname, "../../../data/baltic_it_skills.db");

const db = new Database(dbPath, {
  fileMustExist: true,
});

const NOMINATIM_URL = "https://nominatim.openstreetmap.org/search";
const DELAY_MS = 1200;

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function geocodeCity(city) {
  const url = new URL(NOMINATIM_URL);

  url.searchParams.set("q", city);
  url.searchParams.set("format", "jsonv2");
  url.searchParams.set("addressdetails", "1");
  url.searchParams.set("limit", "5");

  const response = await fetch(url, {
    headers: {
      "User-Agent":
        "BalticITSkills-Thesis/1.0 (https://github.com/JekaterinaShashkina/Baltic_IT_Skills)",
      "Accept-Language": "en",
    },
  });

  if (!response.ok) {
    throw new Error(`Nominatim HTTP ${response.status}`);
  }

  const results = await response.json();

  const places = results
    .filter((place) => ["city", "town", "village"].includes(place.addresstype))
    .sort((a, b) => b.importance - a.importance);

  if (places.length === 0) {
    return { status: "not_found" };
  }

  const exactMatches = places.filter(
    (place) => place.name?.toLocaleLowerCase() === city.toLocaleLowerCase(),
  );

  if (exactMatches.length !== 1) {
    return { status: "ambiguous" };
  }

  const place = exactMatches[0];

  return {
    status: "resolved",
    country: place.address?.country || null,
    latitude: Number(place.lat),
    longitude: Number(place.lon),
  };
}

async function main() {
  const pendingCities = db
    .prepare(
      `
      SELECT city
      FROM job_locations
      WHERE status = 'pending'
      ORDER BY city
    `,
    )
    .all();

  const updateLocation = db.prepare(`
    UPDATE job_locations
    SET country = ?,
        latitude = ?,
        longitude = ?,
        status = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE city = ?
  `);

  console.log(`Cities to geocode: ${pendingCities.length}`);

  for (const [index, { city }] of pendingCities.entries()) {
    try {
      const result = await geocodeCity(city);

      updateLocation.run(
        result.country ?? null,
        result.latitude ?? null,
        result.longitude ?? null,
        result.status,
        city,
      );

      console.log(
        `[${index + 1}/${pendingCities.length}] ${city}: ${result.status}`,
      );
    } catch (error) {
      console.error(`${city}: ${error.message}`);
      // Оставляем pending для повторного запуска.
    }

    if (index < pendingCities.length - 1) {
      await sleep(DELAY_MS);
    }
  }

  console.log("Geocoding finished.");
}

main().catch(console.error);

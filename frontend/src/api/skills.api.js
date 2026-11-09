export const getSkillStatistics = async (country = "") => {
  const params = new URLSearchParams();

  if (country) {
    params.set("country", country);
  }

  const query = params.toString();
  const url = `/api/skills/statistics${query ? `?${query}` : ""}`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error("Failed to fetch skill statistics");
  }

  return response.json();
};

export const getCountryComparison = async () => {
  const countries = ["estonia", "latvia", "lithuania"];

  const results = await Promise.all(
    countries.map((country) => getSkillStatistics(country)),
  );

  return {
    estonia: results[0],
    latvia: results[1],
    lithuania: results[2],
  };
};

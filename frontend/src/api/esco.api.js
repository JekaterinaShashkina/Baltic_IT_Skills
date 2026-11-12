const API_URL = "http://localhost:3001/api/skills";

export const getSkillOccupations = async (skillId, signal) => {
  const response = await fetch(
    `${API_URL}/${encodeURIComponent(skillId)}/occupations`,
    { signal },
  );

  if (!response.ok) {
    throw new Error("Failed to fetch ESCO occupations");
  }

  return response.json();
};

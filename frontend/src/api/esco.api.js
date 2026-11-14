import { ESCO_API_URL, SKILLS_API_URL } from "../config/const";

export const getSkillOccupations = async (skillId, signal) => {
  const response = await fetch(
    `${SKILLS_API_URL}/${encodeURIComponent(skillId)}/occupations`,
    { signal },
  );

  if (!response.ok) {
    throw new Error("Failed to fetch ESCO occupations");
  }

  return response.json();
};

export const getEscoAnalysis = async (signal) => {
  const response = await fetch(`${ESCO_API_URL}/analysis`, {
    signal,
  });

  if (!response.ok) {
    throw new Error("Failed to fetch ESCO analysis");
  }

  return response.json();
};

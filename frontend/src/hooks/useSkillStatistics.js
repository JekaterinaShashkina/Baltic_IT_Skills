import { useEffect, useState } from "react";
import { getSkillStatistics } from "../api/skills.api";

export const useSkillStatistics = (country = "") => {
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;

    const loadStatistics = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await getSkillStatistics(country);

        if (active) {
          setSkills(data);
        }
      } catch (err) {
        if (active) {
          setError(err.message);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    loadStatistics();

    return () => {
      active = false;
    };
  }, [country]);

  return { skills, loading, error };
};

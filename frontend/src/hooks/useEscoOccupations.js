import { useEffect, useState } from "react";
import { getSkillOccupations } from "../api/esco.api";

export const useEscoOccupations = (skillId) => {
  const [occupations, setOccupations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (skillId == null) {
      return;
    }

    const controller = new AbortController();

    const loadOccupations = async () => {
      setLoading(true);
      setError(null);
      setOccupations([]);

      try {
        const data = await getSkillOccupations(skillId, controller.signal);

        if (!controller.signal.aborted) {
          setOccupations(data);
        }
      } catch (err) {
        if (!controller.signal.aborted) {
          setError(err.message);
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    };

    loadOccupations();

    return () => controller.abort();
  }, [skillId]);

  return { occupations, loading, error };
};

import { useEffect, useState } from "react";
import { getJobCounts } from "../api/jobs.api";

export const useDatasetOverview = () => {
  const [counts, setCounts] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadCounts = async () => {
      try {
        const result = await getJobCounts();
        setCounts(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadCounts();
  }, []);

  return { counts, loading, error };
};

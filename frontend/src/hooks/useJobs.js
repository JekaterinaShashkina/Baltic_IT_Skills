import { useEffect, useState } from "react";
import { getJobs } from "../api/jobs.api";

export const useJobs = (page, country) => {
  const [jobs, setJobs] = useState([]);
  const [pagination, setPagination] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;

    const loadJobs = async () => {
      setLoading(true);
      setError(null);

      try {
        const result = await getJobs({
          page,
          limit: 20,
          country,
        });

        if (!active) return;

        setJobs(result.data);
        setPagination(result.pagination);
      } catch (error) {
        if (active) {
          setError(error.message);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    loadJobs();

    return () => {
      active = false;
    };
  }, [page, country]);

  return { jobs, pagination, loading, error };
};

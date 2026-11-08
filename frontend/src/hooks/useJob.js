import { useEffect, useState } from "react";
import { getJobById } from "../api/jobs.api";

export const useJob = (jobId) => {
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;

    const loadJob = async () => {
      setLoading(true);
      setError(null);
      setJob(null);

      try {
        const data = await getJobById(jobId);

        if (active) {
          setJob(data);
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

    loadJob();

    return () => {
      active = false;
    };
  }, [jobId]);

  return { job, loading, error };
};

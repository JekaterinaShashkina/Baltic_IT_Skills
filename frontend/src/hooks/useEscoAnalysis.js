import { useEffect, useState } from "react";
import { getEscoAnalysis } from "../api/esco.api";

export const useEscoAnalysis = () => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const controller = new AbortController();

    const loadAnalysis = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await getEscoAnalysis(controller.signal);

        if (!controller.signal.aborted) {
          setAnalysis(data);
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

    loadAnalysis();

    return () => controller.abort();
  }, []);

  return { analysis, loading, error };
};

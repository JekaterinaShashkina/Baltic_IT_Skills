import { useEscoAnalysis } from "../../hooks/useEscoAnalysis";
import { EscoCoverage } from "./esco/EscoCoverage";
import { EscoCountryComparison } from "./esco/EscoCountryComparison";
import { EscoRelationsChart } from "./esco/EscoRelationsChart";

export const EscoDashboard = () => {
  const { analysis, loading, error } = useEscoAnalysis();

  if (loading) return <p>Loading ESCO statistics...</p>;
  if (error) return <p role="alert">Error: {error}</p>;
  if (!analysis) return <p>No ESCO data available.</p>;

  return (
    <div className="esco-dashboard">
      <EscoCoverage coverage={analysis.coverage} />
      <div className="esco-dashboard__charts">
        <EscoCountryComparison countries={analysis.countryCoverage} />
        <EscoRelationsChart relations={analysis.relations} />
      </div>
    </div>
  );
};

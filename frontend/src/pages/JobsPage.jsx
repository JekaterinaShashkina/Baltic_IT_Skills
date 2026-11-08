import { useState } from "react";
import { useJobs } from "../hooks/useJobs";
import { JobList } from "../components/JobList";
import { CountryFilter } from "../components/CountryFilter";
import { Pagination } from "../components/Pagination";

export const JobsPage = () => {
  const [page, setPage] = useState(1);
  const [country, setCountry] = useState("");

  const { jobs, pagination, loading, error } = useJobs(page, country);

  const handleCountryChange = (selectedCountry) => {
    setCountry(selectedCountry);
    setPage(1);
  };

  return (
    <main className="page-content">
      <section className="job-section">
        <div className="page-intro">
          <h1>Explore IT opportunities</h1>
          <p>
            Discover IT job opportunities across Estonia, Latvia and Lithuania.
          </p>
        </div>

        <div className="jobs-header">
          <h2>Available jobs</h2>

          <CountryFilter
            country={country}
            onCountryChange={handleCountryChange}
          />
        </div>

        {loading && <p>Loading jobs...</p>}
        {error && <p role="alert">Error: {error}</p>}
        {!loading && !error && (
          <>
            <JobList jobs={jobs} />
            <Pagination pagination={pagination} onPageChange={setPage} />
          </>
        )}
      </section>
    </main>
  );
};

const API_URL = "/api/jobs";

export const getJobs = async ({ page = 1, limit = 20, country = "" } = {}) => {
  const params = new URLSearchParams({
    page: String(page),
    limit: String(limit),
  });

  if (country) {
    params.set("country", country);
  }

  const response = await fetch(`${API_URL}?${params}`);

  if (!response.ok) {
    throw new Error("Failed to fetch jobs");
  }

  return response.json();
};

export const getJobById = async (jobId) => {
  const response = await fetch(`${API_URL}/${encodeURIComponent(jobId)}`);

  if (!response.ok) {
    throw new Error("Failed to fetch job");
  }

  return response.json();
};

export const matchJobSkills = async (jobId, skillIds) => {
  const response = await fetch(
    `${API_URL}/${encodeURIComponent(jobId)}/match`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ skillIds }),
    },
  );

  if (!response.ok) {
    throw new Error("Failed to compare skills");
  }

  return response.json();
};

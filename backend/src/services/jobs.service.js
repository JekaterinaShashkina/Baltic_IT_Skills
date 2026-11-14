const jobsRepository = require("../repositories/jobs.repository");

const getAllJobs = (page = 1, limit = 20, country = null) => {
  const offset = (page - 1) * limit;

  const jobs = jobsRepository.getAllJobs(limit, offset, country);
  const total = jobsRepository.countJobs(country);

  return {
    data: jobs,
    pagination: {
      page,
      limit,
      total,
      totalPages: Math.ceil(total / limit),
    },
  };
};

const getJobById = (jobId) => {
  const job = jobsRepository.getJobById(jobId);

  if (!job) {
    return null;
  }

  const skills = jobsRepository.getJobSkills(jobId);

  return {
    ...job,
    skills,
  };
};

const matchJobSkills = (jobId, skillIds) => {
  const job = getJobById(jobId);

  if (!job) {
    return null;
  }

  const studentSkills = new Set(skillIds);

  const matchedSkills = job.skills.filter((skill) =>
    studentSkills.has(skill.skill_id),
  );

  const missingSkills = job.skills.filter(
    (skill) => !studentSkills.has(skill.skill_id),
  );

  const totalRequired = job.skills.length;

  const matchPercentage =
    totalRequired === 0
      ? 0
      : Math.round((matchedSkills.length / totalRequired) * 100);

  return {
    jobId: job.job_id,
    totalRequired,
    matchedCount: matchedSkills.length,
    missingCount: missingSkills.length,
    matchPercentage,
    matchedSkills,
    missingSkills,
  };
};

const recommendJobs = (skillIds, excludeJobId = null, limit = 3) => {
  if (!Array.isArray(skillIds) || skillIds.length === 0) {
    return [];
  }

  const candidates = jobsRepository.getJobsBySkills(skillIds, excludeJobId);

  const recommendations = candidates
    .map((job) => {
      const match = matchJobSkills(job.job_id, skillIds);

      if (!match || match.matchedCount === 0) {
        return null;
      }

      return {
        jobId: job.job_id,
        title: job.title,
        company: job.company,
        matchPercentage: match.matchPercentage,
        matchedCount: match.matchedCount,
        totalRequired: match.totalRequired,
      };
    })
    .filter(Boolean)
    .sort(
      (a, b) =>
        b.matchPercentage - a.matchPercentage ||
        b.matchedCount - a.matchedCount,
    );

  return recommendations.slice(0, limit);
};

const getJobMap = (country = null) => {
  const jobs = jobsRepository.getJobsForMap();
  const locations = jobsRepository.getJobLocations();

  const locationMap = new Map(
    locations.map((location) => [location.city.toLocaleLowerCase(), location]),
  );

  const cityMap = new Map();

  for (const job of jobs) {
    const sourceCountries = (job.source_countries || "")
      .split(",")
      .map((value) => value.trim().toLowerCase())
      .filter(Boolean);

    if (country && !sourceCountries.includes(country.toLowerCase())) {
      continue;
    }

    const cities = new Set(
      job.location
        .split(",")
        .map((city) => city.trim())
        .filter(Boolean),
    );

    for (const city of cities) {
      const location = locationMap.get(city.toLocaleLowerCase());

      if (!location) continue;

      if (!cityMap.has(location.city)) {
        cityMap.set(location.city, {
          city: location.city,
          country: location.country,
          latitude: location.latitude,
          longitude: location.longitude,
          status: location.status,
          jobCount: 0,
          jobs: [],
        });
      }

      const entry = cityMap.get(location.city);

      entry.jobs.push({
        jobId: job.job_id,
        title: job.title,
        sourceCountries,
      });

      entry.jobCount += 1;
    }
  }

  return [...cityMap.values()].sort((a, b) => b.jobCount - a.jobCount);
};

module.exports = {
  getAllJobs,
  getJobById,
  matchJobSkills,
  getJobMap,
  recommendJobs,
};

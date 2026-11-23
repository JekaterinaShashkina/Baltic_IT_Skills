export const prepareCountryComparison = (data, metric = "count") => {
  if (!data) return [];

  const skills = new Map();

  for (const [country, countrySkills] of Object.entries(data)) {
    for (const skill of countrySkills) {
      if (!skills.has(skill.skill_id)) {
        skills.set(skill.skill_id, {
          skill: skill.name,

          estonia: 0,
          latvia: 0,
          lithuania: 0,

          estonia_percentage: 0,
          latvia_percentage: 0,
          lithuania_percentage: 0,
        });
      }

      const item = skills.get(skill.skill_id);

      item[country] = skill.job_count;
      item[`${country}_percentage`] = skill.percentage ?? 0;
    }
  }

  return [...skills.values()]
    .sort((a, b) => {
      if (metric === "percentage") {
        return (
          b.estonia_percentage +
          b.latvia_percentage +
          b.lithuania_percentage -
          (a.estonia_percentage + a.latvia_percentage + a.lithuania_percentage)
        );
      }

      return (
        b.estonia +
        b.latvia +
        b.lithuania -
        (a.estonia + a.latvia + a.lithuania)
      );
    })
    .slice(0, 10);
};

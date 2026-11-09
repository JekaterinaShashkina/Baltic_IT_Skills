export const prepareCountryComparison = (data) => {
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
        });
      }

      skills.get(skill.skill_id)[country] = skill.job_count;
    }
  }

  return [...skills.values()]
    .sort(
      (a, b) =>
        b.estonia +
        b.latvia +
        b.lithuania -
        (a.estonia + a.latvia + a.lithuania),
    )
    .slice(0, 10);
};

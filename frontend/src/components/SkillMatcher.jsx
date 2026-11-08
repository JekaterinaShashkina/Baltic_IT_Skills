import { useState } from "react";
import { matchJobSkills } from "../api/jobs.api";

export const SkillMatcher = ({ job }) => {
  const [selectedSkills, setSelectedSkills] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const toggleSkill = (skillId) => {
    setSelectedSkills((current) =>
      current.includes(skillId)
        ? current.filter((id) => id !== skillId)
        : [...current, skillId],
    );

    setResult(null);
  };

  const handleCompare = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await matchJobSkills(job.job_id, selectedSkills);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="skill-matcher">
      <h2>Compare your skills</h2>
      <p>Select the skills you already have:</p>

      <div className="skill-options">
        {job.skills.map((skill) => (
          <label key={skill.skill_id} className="skill-option">
            <input
              type="checkbox"
              checked={selectedSkills.includes(skill.skill_id)}
              onChange={() => toggleSkill(skill.skill_id)}
            />
            {skill.name}
          </label>
        ))}
      </div>

      <button
        type="button"
        onClick={handleCompare}
        disabled={loading}
        className="compare-button"
      >
        {loading ? "Comparing..." : "Compare skills"}
      </button>

      {error && <p role="alert">Error: {error}</p>}

      {result && (
        <div className="match-result">
          <h3>Your match: {result.matchPercentage}%</h3>

          <div
            className="match-progress"
            role="progressbar"
            aria-label="Skill match percentage"
            aria-valuenow={result.matchPercentage}
            aria-valuemin={0}
            aria-valuemax={100}
          >
            <div
              className="match-progress__fill"
              style={{ width: `${result.matchPercentage}%` }}
            />
          </div>

          <p>
            Matched skills: {result.matchedCount} of {result.totalRequired}
          </p>

          <h4>Missing skills</h4>

          {result.missingSkills.length > 0 ? (
            <ul>
              {result.missingSkills.map((skill) => (
                <li key={skill.skill_id}>{skill.name}</li>
              ))}
            </ul>
          ) : (
            <p>You have all the listed skills!</p>
          )}
        </div>
      )}
    </section>
  );
};

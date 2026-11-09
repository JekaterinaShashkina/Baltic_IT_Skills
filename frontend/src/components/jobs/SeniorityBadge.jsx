const getSeniorities = (value) => {
  if (Array.isArray(value)) {
    return value;
  }

  if (!value) {
    return [];
  }

  try {
    const parsed = JSON.parse(value);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
};

export const SeniorityBadge = ({ seniorities }) => {
  const levels = getSeniorities(seniorities);

  if (levels.length === 0) {
    return null;
  }

  return (
    <div className="seniority-list">
      {levels.map((level) => (
        <span
          key={level}
          className={`seniority-badge seniority-badge--${level.toLowerCase()}`}
        >
          {level}
        </span>
      ))}
    </div>
  );
};

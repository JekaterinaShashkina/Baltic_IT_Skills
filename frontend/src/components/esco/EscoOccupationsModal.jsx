import { useEscoOccupations } from "../../hooks/useEscoOccupations";
import { useScrollLock } from "../../hooks/useScrollLock";
import "./EscoOccupationsModal.css";

export const EscoOccupationsModal = ({
  skill,
  showAll,
  onToggleShowAll,
  onClose,
}) => {
  const { occupations, loading, error } = useEscoOccupations(skill?.skill_id);

  if (!skill) return null;

  const visibleOccupations = showAll ? occupations : occupations.slice(0, 5);

  useScrollLock();

  return (
    <div className="esco-modal__overlay" onClick={onClose}>
      <div
        className="esco-modal"
        role="dialog"
        aria-modal="true"
        aria-label={`ESCO occupations for ${skill.name}`}
        onClick={(event) => event.stopPropagation()}
      >
        <div className="esco-modal__header">
          <div>
            <h2>{skill.name}</h2>
            <p>ESCO skill: {skill.esco_title || skill.name}</p>
          </div>

          <button
            type="button"
            className="esco-modal__close"
            onClick={onClose}
            aria-label="Close"
          >
            ×
          </button>
        </div>

        <h3>Related ICT occupations</h3>

        {loading && <p>Loading occupations...</p>}

        {error && <p role="alert">{error}</p>}

        {!loading && !error && occupations.length === 0 && (
          <p>No related ICT occupations found.</p>
        )}

        {!loading && !error && occupations.length > 0 && (
          <>
            <div className="esco-modal__list">
              {visibleOccupations.map((occupation) => (
                <div
                  key={occupation.occupation_uri}
                  className="esco-modal__occupation"
                >
                  <a
                    href={occupation.occupation_uri}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {occupation.occupation_title}
                  </a>

                  <span
                    className={`esco-modal__relation ${
                      occupation.relation_type === "essential"
                        ? "esco-modal__relation--essential"
                        : ""
                    }`}
                  >
                    {occupation.relation_type || "Not specified"}
                  </span>
                </div>
              ))}
            </div>

            {occupations.length > 5 && (
              <button
                type="button"
                className="esco-modal__show-more"
                onClick={onToggleShowAll}
              >
                {showAll
                  ? "Show less"
                  : `Show all ${occupations.length} occupations`}
              </button>
            )}
          </>
        )}
      </div>
    </div>
  );
};

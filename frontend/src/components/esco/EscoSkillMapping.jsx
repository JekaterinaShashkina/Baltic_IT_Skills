import { EscoOccupationsModal } from "./EscoOccupationsModal";
import { useEscoModal } from "../../hooks/useEscoModal";

export const EscoSkillMapping = ({ skills = [] }) => {
  if (skills.length === 0) {
    return (
      <>
        <h2>Required skills</h2>
        <p>No skills listed for this job.</p>
      </>
    );
  }

  const matchedCount = skills.filter(
    (skill) => skill.mapping_status === "exact",
  ).length;

  const percentage = Math.round((matchedCount / skills.length) * 100);

  const { selectedSkill, showAll, openModal, closeModal, toggleShowAll } =
    useEscoModal();

  return (
    <section className="esco-skills">
      <div className="esco-skills__header">
        <h2>Required skills</h2>

        <span className="esco-skills__summary">
          {matchedCount} of {skills.length} exact ESCO matches
          {" · "}
          {percentage}%
        </span>
      </div>

      <div className="skill-list">
        {skills.map((skill) => {
          const isMatched = skill.mapping_status === "exact";

          return isMatched ? (
            <button
              key={skill.skill_id}
              type="button"
              className="skill-tag esco-skills__matched skill-tag"
              onClick={() => openModal(skill)}
              title={`ESCO: ${skill.esco_title || skill.name}`}
            >
              {skill.name}
            </button>
          ) : (
            <span key={skill.skill_id} className="skill-tag">
              {skill.name}
            </span>
          );
        })}
      </div>

      <p className="esco-skills__note">
        Highlighted skills have an exact ESCO match. Hover over them to see the
        ESCO name.
      </p>
      {selectedSkill && (
        <EscoOccupationsModal
          key={selectedSkill.skill_id}
          skill={selectedSkill}
          showAll={showAll}
          onToggleShowAll={toggleShowAll}
          onClose={() => closeModal(null)}
        />
      )}
    </section>
  );
};

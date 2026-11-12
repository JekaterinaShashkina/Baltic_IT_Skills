import { useState } from "react";

export const useEscoModal = () => {
  const [selectedSkill, setSelectedSkill] = useState(null);
  const [showAll, setShowAll] = useState(false);

  const openModal = (skill) => {
    setSelectedSkill(skill);
    setShowAll(false);
  };

  const closeModal = () => {
    setSelectedSkill(null);
    setShowAll(false);
  };

  const toggleShowAll = () => {
    setShowAll((previous) => !previous);
  };

  return {
    selectedSkill,
    showAll,
    openModal,
    closeModal,
    toggleShowAll,
  };
};

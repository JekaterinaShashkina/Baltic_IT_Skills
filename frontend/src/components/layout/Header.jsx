import { NavLink } from "react-router-dom";
import { JOBS_ROUTE, STATISTICS_ROUTE } from "../../config/const";

export const Header = () => {
  return (
    <header className="site-header">
      <div className="site-header__inner">
        <div className="site-brand">
          <span className="site-brand__icon">{"</>"}</span>
          <span>Baltic IT Skills</span>
        </div>

        <nav className="site-nav" aria-label="Main navigation">
          <NavLink to={JOBS_ROUTE} className="site-nav__link">
            Jobs
          </NavLink>

          <NavLink to={STATISTICS_ROUTE} className="site-nav__link">
            Statistics
          </NavLink>
        </nav>
      </div>
    </header>
  );
};

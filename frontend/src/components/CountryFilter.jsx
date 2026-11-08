export const CountryFilter = ({ country, onCountryChange }) => {
  return (
    <div className="country-filter">
      <label htmlFor="country">Country</label>

      <select
        id="country"
        value={country}
        onChange={(event) => onCountryChange(event.target.value)}
      >
        <option value="">All countries</option>
        <option value="estonia">Estonia</option>
        <option value="latvia">Latvia</option>
        <option value="lithuania">Lithuania</option>
      </select>
    </div>
  );
};

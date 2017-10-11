/* global gettext */
/* eslint react/no-array-index-key: 0 */

import React from 'react';
import PropTypes from 'prop-types';


class ShowErrors extends React.Component {

  componentDidMount() {
    window.scrollTo(0, 0);
  }

  render() {
    return this.props.errorList.length > 0 &&
      <div className="col-sm-12">
        <div className="alert alert-danger" role="alert">
          <strong>{gettext('Please fix following errors:')}</strong>
          <ul>
            {this.props.errorList.map(error =>
              <li>{error}</li>,
            )}
          </ul>
        </div>
      </div>;
  }
}


ShowErrors.propTypes = {
  errorList: PropTypes.arrayOf(PropTypes.object).isRequired,
};

export default ShowErrors;

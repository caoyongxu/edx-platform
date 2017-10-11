/* global gettext */

import React from 'react';
import PropTypes from 'prop-types';


class FileUpload extends React.Component {

  static removeFile(e) {
    e.preventDefault();
    const fileToken = e.target.id;
    const fileRow = $(e.target).closest('.row');
    const url = `https://arbisoft.zendesk.com/api/v2/uploads/${fileToken}.json`;
    const accessToken = 'd6ed06821334b6584dd9607d04007c281007324ed07e087879c9c44835c684da';
    const request = new XMLHttpRequest();

    request.open('DELETE', url, true);
    request.setRequestHeader('Authorization', `Bearer ${accessToken}`);
    request.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');

    request.send();

    request.onreadystatechange = function removeFile() {
      if (request.readyState === 4 && request.status === 204) {
        fileRow.fadeOut();
      }
    };
  }

  render() {
    return (
      <div>
        {
          this.props.fileList.map(file =>
            (<div key={file.fileToken} className="row">
              <div className="col-sm-12">
                <span className="file-name">{file.fileName}</span>
                <span className="file-action remove-upload">
                  <button id={file.fileToken} onClick={FileUpload.removeFile}>{gettext('Remove file')}</button>
                </span>
              </div>
            </div>),
          )
        }
      </div>
    );
  }
}

FileUpload.propTypes = {
  fileList: PropTypes.arrayOf(PropTypes.object).isRequired,
};
export default FileUpload;

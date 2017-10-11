/* global gettext */
/* eslint one-var: ["error", "always"] */
/* eslint no-alert: "error" */


import PropTypes from 'prop-types';
import React from 'react';
import ReactDOM from 'react-dom';

import FileUpload from './file_upload';
import ShowErrors from './errors_list';
import ShowProgress from './upload_progress';
import LoggedInUser from './login_user';
import LoggedOutUser from './logged_out_user';

// TODO
// edx zendesk APIs
// access token
// custom fields ids
// https://openedx.atlassian.net/browse/LEARNER-2736
// https://openedx.atlassian.net/browse/LEARNER-2735

class RenderForm extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      fileList: [],
      fileInProgress: null,
      currentRequest: null,
      errorList: [],
    };
    this.uploadFile = this.uploadFile.bind(this);
    this.submitForm = this.submitForm.bind(this);
  }

  uploadFile(e) {
    const url = 'https://arbisoft.zendesk.com/api/v2/uploads.json?filename=',
      fileReader = new FileReader(),
      request = new XMLHttpRequest(),
      errorList = [],
      $this = this,
      file = e.target.files[0],
      accessToken = 'd6ed06821334b6584dd9607d04007c281007324ed07e087879c9c44835c684da',
      maxFileSize = 5000000,  // 5mb is max limit
      allowedFileTypes = ['gif', 'png', 'jpg', 'jpeg', 'pdf'];

    // remove file from input and upload it to zendesk after validation
    $(e.target).val('');
    this.setState({
      errorList: [],
    });

    if (file.size > maxFileSize) {
      errorList.push(gettext('Please select file of less than 5 MB!'));
    } else if ($.inArray(file.name.split('.').pop().toLowerCase(), allowedFileTypes) === -1) {
      errorList.push(gettext('Please select image or pdf file!'));
    }

    if (errorList.length > 0) {
      this.setState({
        errorList,
      });
      return;
    }

    request.open('POST', (url + file.name), true);
    request.setRequestHeader('Authorization', `Bearer ${accessToken}`);
    request.setRequestHeader('Content-Type', 'image/jpeg');

    fileReader.readAsArrayBuffer(file);

    fileReader.onloadend = function success() {
      $this.setState({
        fileInProgress: file.name,
        currentRequest: request,
      });
      request.send(fileReader.result);
    };

    request.upload.onprogress = function renderProgress(event) {
      if (event.lengthComputable) {
        const percentComplete = (event.loaded / event.total) * 100;
        $('.progress-bar-striped').css({ width: `${percentComplete}%` });
      }
    };

    request.onreadystatechange = function success() {
      if (request.readyState === 4 && request.status === 201) {
        const uploadedFile = {
          fileName: file.name,
          fileToken: JSON.parse(request.response).upload.token,
        };

        $this.setState(
          {
            fileList: $this.state.fileList.concat(uploadedFile),
            fileInProgress: null,
          },
        );
      }
    };

    request.onabort = function abortUpload() {
      $this.setState({
        fileInProgress: null,
      });
    };
  }

  submitForm() {
    const url = 'https://arbisoft.zendesk.com/api/v2/tickets.json',
      $userInfo = $('.user-info'),
      request = new XMLHttpRequest(),
      $course = $('#course'),
      accessToken = 'd6ed06821334b6584dd9607d04007c281007324ed07e087879c9c44835c684da',
      data = {
        subject: $('#subject').val(),
        comment: {
          body: $('#message').val(),
          uploads: $.map($('.uploaded-files a'), n => n.id),
        },
      };

    let course;

    if ($userInfo.length) {
      data.requester = $userInfo.data('email');
      course = $course.find(':selected').text();
      if (!course.length) {
        course = $course.val();
      }
    } else {
      data.requester = $('#email').val();
      course = $course.val();
    }

    data.custom_fields = [{
      id: '114099484092',
      value: course,
    }];

    if (this.validateData(data)) {
      request.open('POST', url, true);
      request.setRequestHeader('Authorization', `Bearer ${accessToken}`);
      request.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');

      request.send(JSON.stringify({
        ticket: data,
      }));

      request.onreadystatechange = function success() {
        if (request.readyState === 4 && request.status === 201) {
          // TODO needs to remove after implementing success page
          const alert = 'request submited successfully.';
          alert();
        }
      };
    }
  }


  validateData(data) {
    const errors = [],
      regex = /^([a-zA-Z0-9_.+-])+@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;

    if (!data.subject) {
      errors.push(gettext('You must enter a subject before submitting.'));
      $('#subject').closest('.form-group').addClass('has-error');
    }
    if (!data.comment.body) {
      errors.push(gettext('You must enter a message before submitting.'));
      $('#message').closest('.form-group').addClass('has-error');
    }
    if (!data.requester) {
      errors.push(gettext('You must enter email before submitting.'));
      $('#email').closest('.form-group').addClass('has-error');
    } else if (!regex.test(data.requester)) {
      errors.push(gettext('You must enter a valid email before submitting.'));
      $('#email').closest('.form-group').addClass('has-error');
    }

    if (!errors.length) {
      return true;
    }

    this.setState({
      errorList: errors,
    });
    return false;
  }

  render() {
    let userElement;
    if (this.props.context.user) {
      userElement = <LoggedInUser userInformation={this.props.context.user} />;
    } else {
      userElement = <LoggedOutUser loginUrl={this.props.context.loginQuery} />;
    }

    return (
      <div className="contact-us-wrapper">

        <div className="row">
          <div className="col-sm-12">
            <h2>{gettext('Contact Us')}</h2>
          </div>
        </div>

        <div className="row form-errors">
          <ShowErrors errorList={this.state.errorList} />
        </div>

        <div className="row">
          <div className="col-sm-12">
            <p>{gettext('Your question may have already been answered.')}</p>
          </div>
        </div>

        <div className="row">
          <div className="col-sm-12">
            <a
              href={this.props.context.marketingUrl}
              className="btn btn-secondary help-button"
            >{gettext('Visit edX Help')}</a>
          </div>
        </div>

        {userElement}

        <div className="row">
          <div className="col-sm-12">
            <div className="form-group">
              <label htmlFor="subject">{gettext('Subject')}</label>
              <input type="text" className="form-control" id="subject" />
            </div>
          </div>
        </div>

        <div className="row">
          <div className="col-sm-12">
            <div className="form-group">
              <label htmlFor="message">{gettext('Message')}</label>
              <p
                className="message-desc"
              >{gettext('The more you tell us, the more quickly and helpfully we can respond!')}</p>
              <textarea
                aria-describedby="message-desc"
                className="form-control"
                rows="7"
                id="message"
              />
            </div>
          </div>
        </div>


        <div className="file-container">
          <div className="row">
            <div className="col-sm-12">
              <div className="form-group">
                <label htmlFor="attachment">{gettext('Add Attachment')}
                  <span> {gettext('(Optional)')}</span>
                </label>
                <input
                  id="attachment"
                  className="file file-loading"
                  type="file"
                  accept=".pdf, .jpeg, .png, .jpg, .gif"
                  onChange={this.uploadFile}
                />
              </div>
            </div>
          </div>
          <div className="progress-container">
            {this.state.fileInProgress &&
            <ShowProgress
              fileName={this.state.fileInProgress}
              request={this.state.currentRequest}
            />
            }
          </div>
          <div className="uploaded-files">
            {this.state.fileList.length > 0 &&
            <FileUpload fileList={this.state.fileList} />
            }
          </div>
        </div>

        <div className="row">
          <div className="col-sm-12">
            <button
              className="btn btn-primary btn-submit"
              onClick={this.submitForm}
            >{gettext('Submit')}</button>
          </div>
        </div>

      </div>

    );
  }
}

RenderForm.propTypes = {
  context: PropTypes.arrayOf(PropTypes.object).isRequired,
};


export class SingleSupportForm {
  constructor(context) {
    ReactDOM.render(
      <RenderForm context={context} />,
      document.getElementById('root'),
    );
  }
}

import React from 'react';
import { Formik, Form, Field } from 'formik';
import { withRouter } from 'react-router-dom';
import * as yup from 'yup';
import PropTypes from 'prop-types';
import { reset } from '../../utils/auth_api';

// define the validation schema for the input fields
const validationSchema = yup.object().shape({
  password: yup
    .string()
    .min(8, 'password must be at least 8 characters')
    .max(256, 'password must be at most 256 characters')
    .required(),
  passwordConf: yup.string().oneOf([yup.ref('password'), null], 'passwords must match')
});

/**
 * This form handles password reset
 */
export const handleReset = async (props, values, { setErrors, setSubmitting }) => {
  const { history } = props;
  const { password } = values;
  const response = await reset(password); // TODO: how to identify which account

  let errors;
  switch (response.data.status_code) {
    case 200:
      history.push('/reset-successful'); // TODO: routing is not final
      return;
    case 400:
      errors = response.data.content.errors; // TODO: might have a different name
      break;
    default:
      errors = { default: 'something unexpected happened' };
  }

  setErrors(errors);
  setSubmitting(false);
};

const LoginForm = props => {
  LoginForm.propTypes = {
    history: PropTypes.object
  };

  const handleSubmit = async (values, options) => {
    await handleReset(props, values, options);
  };

  return (
    <Formik
      initialValues={{ email: '' }}
      validationSchema={validationSchema}
      onSubmit={handleSubmit}
      render={({ errors, touched, status, handleSubmit, isSubmitting }) => (
        <Form onSubmit={handleSubmit}>
          <label>
            <Field type="password" name="password" placeholder="password" />
            {touched.password && errors.password}
          </label>
          <label>
            <Field type="password" name="passwordConf" placeholder="confirm password" />
            {touched.passwordConf && errors.passwordConf}
          </label>
          <button type="submit" disabled={isSubmitting}>
            Submit
          </button>
          <p>{errors.default}</p>
        </Form>
      )}
    />
  );
};

const LoginFormWithRouter = withRouter(LoginForm); // bound react router, to access history
export default LoginFormWithRouter;

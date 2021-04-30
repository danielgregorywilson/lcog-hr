import { MutationTree } from 'vuex';
import { AuthStateInterface } from './state';

const mutation: MutationTree<AuthStateInterface> = {
  // TODO: Remove, old way of logging in
  authRequest: state => {
    state.status = 'loading'
  },
  setAuth: state => {
    state.status = 'loading'
  },
  authSuccess: (state, token: string) => {
    state.status = 'success'
    state.token = token
  },
  authError: state => {
    state.status = 'error'
  },
  authLogout: state => {
    // Clean up state
    state.token = '';
  }
};

export default mutation;

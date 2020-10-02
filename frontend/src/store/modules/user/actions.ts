import { ActionTree } from 'vuex';
import { StateInterface } from '../../index';
import { UserStateInterface } from './state';
import axios from 'axios';

const actions: ActionTree<UserStateInterface, StateInterface> = {
  userRequest: ({ commit, dispatch }) => {
    commit('userRequest');
    axios({ url: 'http://localhost:8000/api/v1/current-user/' })
      .then((resp: {data: {pk: number}}) => {
        commit('userSuccess', resp);
        dispatch('performanceReviewModule/getNextPerformanceReview', {pk: resp.data.pk}, { root: true })
            .catch(err => console.log(err))
      })
      .catch(() => {
        commit('userError');
        // if resp is unauthorized, logout, to
        dispatch('authLogout')
          .catch(err => console.log(err))
      });
  }
};

export default actions;

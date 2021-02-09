import { ActionTree } from 'vuex';
import { StateInterface } from '../../index';
import { TimeOffRequestStateInterface } from './state';
import axios from 'axios';
import { TimeOffRequestCreate } from 'src/store/types';

const actions: ActionTree<TimeOffRequestStateInterface, StateInterface> = {
  getAllTimeOffRequests: ({ commit }) => {
    axios({ url: `${ process.env.API_URL }api/v1/timeoffrequest` }) // eslint-disable-line @typescript-eslint/restrict-template-expressions
      .then(resp => {
        commit('setTimeOffRequests', resp);
      })
      .catch(e => {
        console.log(e)
      });
  },
  createTimeOffRequest: ({ dispatch }, timeOffRequest: TimeOffRequestCreate) => {
    axios({ url: `${ process.env.API_URL }api/v1/timeoffrequest`, data: timeOffRequest, method: 'POST' }) // eslint-disable-line @typescript-eslint/restrict-template-expressions
      .then(() => {
        dispatch('getAllReviewNotes')
          .catch(e => {
            console.log(e)
          })
      })
      .catch(e => {
        console.log(e)
      });
  },
};

export default actions;

import { ActionTree } from 'vuex';
import { StateInterface } from '../../index';
import { PerformanceReviewStateInterface } from './state';
import axios from 'axios';
import { ReviewNoteCreate } from 'src/store/types';

const actions: ActionTree<PerformanceReviewStateInterface, StateInterface> = {
  getNextPerformanceReview: ({ commit }, data: {pk: number}) => {
    axios({ url: `${ process.env.API_URL }api/v1/employee/${data.pk}/employee_next_performance_review`}) // eslint-disable-line @typescript-eslint/restrict-template-expressions
      .then(resp => {
        commit('setNextPerformanceReview', resp)
      })
      .catch(e => {
        console.log(e)
      })
  },
  employeeMarkDiscussed: ({ commit }) => {
    commit('employeeMarkDiscussed')
  },
  getAllReviewNotes: ({ commit }) => {
    axios({ url: `${ process.env.API_URL }api/v1/reviewnote` }) // eslint-disable-line @typescript-eslint/restrict-template-expressions
      .then(resp => {
        commit('setAllReviewNotes', resp);
      })
      .catch(e => {
        console.log(e)
      });
  },
  createReviewNote: ({ dispatch }, reviewNote: ReviewNoteCreate) => {
    axios({ url: `${ process.env.API_URL }api/v1/reviewnote`, data: reviewNote, method: 'POST' }) // eslint-disable-line @typescript-eslint/restrict-template-expressions
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
  getAllPerformanceReviewsActionRequired: ({ commit }) => {
    axios({ url: `${ process.env.API_URL }api/v1/performancereview?action_required=True` }) // eslint-disable-line @typescript-eslint/restrict-template-expressions
      .then(resp => {
        commit('setAllPerformanceReviewsActionRequired', resp);
      })
      .catch(e => {
        console.log(e)
      });
  },
  getAllPerformanceReviewsActionNotRequired: ({ commit }) => {
    axios({ url: `${ process.env.API_URL }api/v1/performancereview?action_required=False` }) // eslint-disable-line @typescript-eslint/restrict-template-expressions
      .then(resp => {
        commit('setAllPerformanceReviewsActionNotRequired', resp);
      })
      .catch(e => {
        console.log(e)
      });
  },
};

export default actions;
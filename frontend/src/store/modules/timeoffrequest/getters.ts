import { GetterTree } from 'vuex';
import { StateInterface } from '../../index';
import { TimeOffRequestStateInterface } from './state';

const getters: GetterTree<TimeOffRequestStateInterface, StateInterface> = {
  allTimeOffRequests: state => state.allTimeOffRequests
};

export default getters;

export interface TimeOffRequestInterface {
  pk: number
  employee_pk: number
  employee_name: string
  manager_pk: number
  date_start: Date
  date_end: Date
  approved: boolean
}

export interface TimeOffRequestStateInterface {
  allTimeOffRequests: Array<TimeOffRequestInterface>
}

const state: TimeOffRequestStateInterface = {
  allTimeOffRequests: [],
};

export default state;

import { AxiosResponse } from 'axios'
import { Url } from 'url'

/////////////////////////////////////////////////////
// Auth Users Structure from Django Rest Framework //
/////////////////////////////////////////////////////

export interface AxiosAuthResponse extends AxiosResponse {
  data: {
    token: string
  }
}

export interface UserRetrieve {
  url: Url
  username: string
  email: string
  name: string
  is_staff: boolean
  is_manager: boolean
  is_upper_manager: boolean
}

export interface AxiosUserRetrieveOneServerResponse {
  data: UserRetrieve
}

///////////////////////////////////////////////////
// Employee Structure from Django Rest Framework //
///////////////////////////////////////////////////

export interface EmployeeRetrieve {
  url: string
  pk: number
  name: string
  user: Url
  email: string
  manager: Url
  is_manager: boolean
  is_upper_manager: boolean
  is_hr_manager: boolean
  is_executive_director: boolean
  prs_can_view: Array<number>
  notes_can_view: Array<number>
  next_to_sign_prs: string
}

export interface AxiosEmployeeRetrieveManyServerResponse {
  data: {
    results: Array<EmployeeRetrieve>
  }
}

////////////////////////////////////////////////////////////
// PerformanceReview Structure from Django Rest Framework //
////////////////////////////////////////////////////////////

export interface PerformanceReviewRetrieve {
  url: Url
  pk: number
  employee_pk: number
  employee_name: string
  employee_division: string
  employee_unit_or_program: string
  employee_job_title: string
  manager_pk: number
  manager_name: string
  days_until_review: number
  status: string
  period_start_date: Date
  period_end_date: Date
  effective_date: Date
  evaluation_type: string
  probationary_evaluation_type: string
  step_increase: string
  top_step_bonus: string
  action_other: string

  factor_job_knowledge: string
  factor_work_quality: string
  factor_work_quantity: string
  factor_work_habits: string
  factor_analysis: string
  factor_initiative: string
  factor_interpersonal: string
  factor_communication: string
  factor_dependability: string
  factor_professionalism: string
  factor_management: string
  factor_supervision: string
  evaluation_successes: string
  evaluation_opportunities: string
  evaluation_goals_manager: string
  evaluation_comments_employee: string
  
  position_description_link: string
  description_reviewed_employee: boolean
  signed_position_description: string
  all_required_signatures: Array<[string, string, string]>
}

export interface AxiosPerformanceReviewRetrieveOneServerResponse {
  data: PerformanceReviewRetrieve
}

export interface AxiosPerformanceReviewRetrieveManyServerResponse {
  data: {
    results: Array<PerformanceReviewRetrieve>
  }
}

export interface PerformanceReviewCreate {
  url: Url
  pk: number
  employee_name: string
  days_until_review: number
  status: string
}

export interface PerformanceReviewUpdate {
  evaluation_type: string
  probationary_evaluation_type: string
  step_increase: string
  top_step_bonus: string
  action_other: string
  factor_job_knowledge: string
  factor_work_quality: string
  factor_work_quantity: string
  factor_work_habits: string
  factor_analysis: string
  factor_initiative: string
  factor_interpersonal: string
  factor_communication: string
  factor_dependability: string
  factor_professionalism: string
  factor_management: string
  factor_supervision: string
  evaluation_successes: string
  evaluation_opportunities: string
  evaluation_goals_manager: string
  evaluation_comments_employee: string
  description_reviewed_employee: boolean
}

export interface PerformanceReviewUpdatePartial {
  evaluation_type?: string
  probationary_evaluation_type?: string
  step_increase?: string
  top_step_bonus?: string
  action_other?: string
  factor_job_knowledge?: string
  factor_work_quality?: string
  factor_work_quantity?: string
  factor_work_habits?: string
  factor_analysis?: string
  factor_initiative?: string
  factor_interpersonal?: string
  factor_communication?: string
  factor_dependability?: string
  factor_professionalism?: string
  factor_management?: string
  factor_supervision?: string
  evaluation_successes?: string
  evaluation_opportunities?: string
  evaluation_goals_manager?: string
  evaluation_comments_employee?: string
  description_reviewed_employee?: boolean
}

export interface AxiosPerformanceReviewUpdateServerResponse {
  data: PerformanceReviewRetrieve
}

export interface AxiosPerformanceReviewSignServerResponse {
  data: {
    signatures: Array<[string, string, string]>
  }
}

export interface SignedPositionDescriptionUpload {
  pk: string
  file: File
}

export interface SignedPositionDescriptionUploadServerResponse {
  data: string
  status: number
  statusText: string
}


/////////////////////////////////////////////////////
// Signature Structure from Django Rest Framework //
/////////////////////////////////////////////////////

export interface SignatureCreate {
  review_pk: number
  employee_pk: number
}

export interface SignatureRetrieve {
  url: Url
  pk: number
  review: Url
  employee: Url
  date: Date
}

// export interface AxiosReviewNoteRetrieveOneServerResponse {
//   data: ReviewNoteRetrieve
// }

// export interface AxiosManagerReviewNotesForEmployeeServerResponse {
//   data: Array<ReviewNoteRetrieve>
// }

// export interface AxiosReviewNoteRetrieveManyServerResponse {
//   data: {
//     results: Array<ReviewNoteRetrieve>
//   }
// }

// export interface AxiosReviewNoteUpdateServerResponse {
//   data: ReviewNoteRetrieve
// }


/////////////////////////////////////////////////////
// ReviewNote Structure from Django Rest Framework //
/////////////////////////////////////////////////////

export interface ReviewNoteCreate {
  employee_pk: number
  note: string
}

export interface ReviewNoteRetrieve {
  url: Url
  pk: number
  employee_pk: number
  employee_name: string
  date: Date
  note: string
}

export interface ReviewNoteUpdate {
  employee_pk?: number
  note?: string
}

export interface AxiosReviewNoteRetrieveOneServerResponse {
  data: ReviewNoteRetrieve
}

export interface AxiosManagerReviewNotesForEmployeeServerResponse {
  data: Array<ReviewNoteRetrieve>
}

export interface AxiosReviewNoteRetrieveManyServerResponse {
  data: {
    results: Array<ReviewNoteRetrieve>
  }
}

export interface AxiosReviewNoteUpdateServerResponse {
  data: ReviewNoteRetrieve
}


/////////////////////////////////////////////////////////
// TimeOffRequest Structure from Django Rest Framework //
/////////////////////////////////////////////////////////

export interface TimeOffRequestRetrieve {
  employee_pk: number
  date_start: Date
  date_end: Date
}

export interface TimeOffRequestRetrieve {
  url: Url
  pk: number
  employee_pk: number
  employee_name: string
  manager_pk: number
  date_start: Date
  date_end: Date
  approved: boolean
}
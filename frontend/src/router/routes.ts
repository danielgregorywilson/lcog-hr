import { Route, RouteConfig } from 'vue-router';

import authState from '../store/modules/auth/state'
import userState from '../store/modules/user/state'

type Next = (path?: string) => void

const ifNotAuthenticated = (to: Route, from: Route, next: Next) => {
  if (!authState.token) { // TODO: This should use the isAuthenticated getter
    next()
    return
  }
  next('/')
}

const ifAuthenticated = (to: Route, from: Route, next: Next) => {
  if (!!authState.token) { // TODO: This should use the isAuthenticated getter
    next()
    return
  }
  next('auth/login')
}

const ifManager = (to: Route, from: Route, next: Next) => {
  if (userState.profile.is_manager) {
    next()
    return
  }
  next('dashboard')
}

const ifCanViewReview = (to: Route, from: Route, next: Next) => {
  if (userState.profile.prs_can_view.indexOf(parseInt(to.params.pk)) != -1) {
    next()
    return
  } else {
    console.info('User can not view PR', to.params.pk, 'Redirecting to dashboard.')
    next('dashboard')
  }
}

const ifCanViewNote = (to: Route, from: Route, next: Next) => {
  if (userState.profile.notes_can_view.indexOf(parseInt(to.params.pk)) != -1) {
    next()
    return
  } else {
    next('dashboard')
  }
}

// TODO: Add a reset password view as in Django version, unless we're authenticating with LDAP
const routes: RouteConfig[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '/', redirect: '/dashboard' },
      {
        path: '/dashboard',
        name: 'dashboard',
        component: () => import('pages/Dashboard.vue'),
      },
      {
        path: '/reviews',
        name: 'reviews',
        component: () => import('pages/PerformanceReviews.vue'),
        beforeEnter: ifManager,
      },
      {
        path: '/note/new',
        name: 'note-create',
        component: () => import('pages/ReviewNoteCreate.vue'),
        beforeEnter: ifManager,
      },
      {
        path: '/note/:pk',
        name: 'note-details',
        component: () => import('pages/ReviewNoteDetail.vue'),
        beforeEnter: ifCanViewNote,
      },
      {
        path: '/pr/:pk',
        name: 'pr-details',
        component: () => import('pages/PerformanceReviewDetail.vue'),
        beforeEnter: ifCanViewReview,
      },
      {
        path: '/timeoff',
        name: 'timeoff',
        component: () => import('pages/TimeOffRequests.vue'),
        beforeEnter: ifAuthenticated,
      },
      {
        path: '/security-message',
        name: 'security-message',
        component: () => import('pages/SecurityMessage.vue'),
        // TODO: Temporary for demonstrating to team
        // beforeEnter: ifAuthenticated,
      }
    ]
  },
  {
    path: '/print',
    component: () => import('layouts/PrintLayout.vue'),
    children: [
      {
        path: 'pr/:pk',
        name: 'pr-print',
        component: () => import('pages/PerformanceReviewDetail.vue'),
        beforeEnter: ifManager,
        props: {
          print: true
        }
      }
    ]
  },
  {
    path: '/auth',
    component: () => import('layouts/AuthLayout.vue'),
    children: [
      {
        path: 'login',
        name: 'login',
        component: () => import('pages/auth/Login.vue'),
        beforeEnter: ifNotAuthenticated,
      },
    ]
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/404',
    component: () => import('pages/Error404.vue')
  },
  {
    path: '*',
    component: () => {
      console.log('Hit the 404')
      return import('pages/Error404.vue')
    }
  }
];

export default routes;

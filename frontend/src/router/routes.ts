import { Route, RouteConfig } from 'vue-router';

import authState from '../store/modules/auth/state'

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
        beforeEnter: ifAuthenticated,
      },
      {
        path: '/reviews',
        name: 'reviews',
        component: () => import('pages/PerformanceReviews.vue'),
        beforeEnter: ifAuthenticated,
      },
      {
        path: '/note/new',
        name: 'note-create',
        component: () => import('pages/ReviewNoteCreate.vue'),
        beforeEnter: ifAuthenticated,
      },
      {
        path: '/note/:pk',
        name: 'note-details',
        component: () => import('pages/ReviewNoteDetail.vue'),
        beforeEnter: ifAuthenticated,
      },
      {
        path: '/pr/:pk',
        name: 'pr-details',
        component: () => import('pages/PerformanceReviewDetail.vue'),
        beforeEnter: ifAuthenticated,
      },
      {
        path: '/timeoff',
        name: 'timeoff',
        component: () => import('pages/TimeOffRequests.vue'),
        beforeEnter: ifAuthenticated,
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
    path: '*',
    component: () => import('pages/Error404.vue')
  }
];

export default routes;
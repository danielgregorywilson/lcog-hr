<template>
  <div id="q-app">
    <router-view />
  </div>
</template>
<script lang="ts">
  import axios from 'axios';

  import { Component, Vue } from 'vue-property-decorator'

  const token = localStorage.getItem('user-token')
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Token ${ token }` // eslint-disable-line @typescript-eslint/no-unsafe-member-access
  }

  export const bus = new Vue()

  @Component
  export default class App extends Vue{}
</script>

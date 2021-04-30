<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          id="menu-button"
          @click="leftDrawerOpen = !leftDrawerOpen"
        />

        <q-toolbar-title>
          <div v-if="name()">
            Hi {{ name() }}
          </div>
        </q-toolbar-title>

        <div>Quasar v{{ $q.version }}</div>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
      content-class="bg-grey-1"
      :width="210"
    >
      <q-list>
        <q-item-label
          header
          class="text-grey-8"
        >
          LCOG HR App
        </q-item-label>
        <q-item
          clickable
          @click='loginWithMicrosoft'
          v-if="!isAuthenticated()"
        >
          <q-item-section avatar>
            <q-img
              id="lcog-logo"
              src="../assets/microsoft-logo.svg"
              style="width: 24px;"
            />
          </q-item-section>
          <q-item-section>
            <q-item-label>Sign in with Microsoft</q-item-label>
          </q-item-section>
        </q-item>
        <div v-if="isAuthenticated()">
          <NavLink
            v-for="link in navLinks"
            :key="link.title"
            v-bind="link"
          />
        </div>
        <q-item
          clickable
          @click='logoutWithMicrosoft'
          v-if="isAuthenticated()"
        >
          <q-item-section avatar>
            <q-icon name='west' />
          </q-item-section>
          <q-item-section>
            <q-item-label>Log Out</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script lang="ts">
import NavLink from 'components/NavLink.vue'

import { Component, Vue } from 'vue-property-decorator'

import { UserAgentApplication } from 'msal';

interface LinkData {
  title: string;
  icon: string;
  link: string;
  managerOnly?: boolean;
}

const linksData: Array<LinkData> = [
  {
    title: 'Dashboard',
    icon: 'dashboard',
    link: '/dashboard'
  },
  {
    title: 'Performance Reviews',
    icon: 'assignment_turned_in',
    link: '/reviews',
    managerOnly: true
  },
  {
    title: 'Time off Requests',
    icon: 'schedule',
    link: '/timeoff'
  },
];

interface LayoutData {
  name: string
}

@Component({
  components: { NavLink }
})
export default class MainLayout extends Vue{
  private leftDrawerOpen = false;
  private navLinks: Array<LinkData> = linksData;
  
  private isAuthenticated(): boolean {
    return this.$store.getters['authModule/isAuthenticated'] // eslint-disable-line @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-unsafe-return
  }
  
  private name() {
    return this.$store.getters['userModule/getEmployeeProfile'].name // eslint-disable-line @typescript-eslint/no-unsafe-member-access, @typescript-eslint/no-unsafe-return
  }

  public getCurrentUser(): void {
    if (this.$store.getters['authModule/isAuthenticated'] && !this.$store.getters['userModule/isProfileLoaded']) { // eslint-disable-line @typescript-eslint/no-unsafe-member-access
      this.$store.dispatch('userModule/userRequest')
        .catch(e => {
          console.error('Error getting user from store', e)
        })
    }
  }

  // For msal.js Azure/AD SSO 
  private msalConfig = {
    auth: {
      clientId: '2c4ec8a0-6be9-4c9c-a6b6-6a40392b8e3e',
      authority: 'https://login.microsoftonline.com/9a80ddb7-1790-4782-a634-ef32f273169c',
      redirectUri: 'http://localhost:8080/dashboard',
    },
    cache: {
      cacheLocation: 'sessionStorage', // This configures where your cache will be stored
      storeAuthStateInCookie: false, // Set this to "true" if you are having issues on IE11 or Edge
    }
  };

  private myMSALObj = new UserAgentApplication(this.msalConfig);

  private loginRequest = {
    scopes: ['openid', 'profile', 'User.Read']
  };

  public loginWithMicrosoft(): void {
    this.myMSALObj.loginPopup(this.loginRequest)
      .then((loginResponse) => {
        console.log('id_token acquired at: ' + new Date().toString());
        console.log(loginResponse);
        
        if (this.myMSALObj.getAccount()) {
          let account = this.myMSALObj.getAccount()
          this.$store.dispatch('authModule/setAuth', { username: account.userName })
            .then(() => this.$router.push('/'))
            .catch((err) => console.log(err))
        }      
      }).catch(function (error) {
          console.log(error);
      });
  }

  public logoutWithMicrosoft() {
    this.$store.dispatch('authModule/authLogout')
    .then(() => {
      this.myMSALObj.logout();
    })
    .catch(e => {
      console.error('Error logging out', e);
    })
  }

  // TODO: Old logout
  public logout(): void {
    this.$store.dispatch('authModule/authLogout')
    .then(() => {
      this.$router.push('/auth/login')
        .catch(e => {
          console.error('Error navigating to login page after logout', e)
        })
    })
    .catch(e => {
      console.error('Error logging out', e);
    })
  }
  mounted() {
    this.getCurrentUser();
  }
};
</script>

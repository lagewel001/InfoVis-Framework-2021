<template>
  <header class="gridx">
    <vs-navbar
      v-model="indexActive"
      v-bind:color="main_color"
      class="topnavbar" text-color="rgba(255,255,255,0.7)" active-text-color="rgba(255,255,255,1)"
    >
      <!---
      Template logo
      -->
      <div slot="title" class="themelogo">
        <img :src="logo" v-if="logo" alt="Dashboard"/>
        <span class="logo-text" v-if="title">{{ title }}</span>
      </div>

      <vs-spacer></vs-spacer>

    </vs-navbar>

  </header>

</template>

<script>
export default {
  name : 'Navbar',
  props: {
    main_color: {
      type: String,
    },
    title: {
          type: String,
    },
    logo: {
        type: String
    },
  },
  data:()=>({
    indexActive: 0,
    showToggle: false
  }),
  methods: {}
}
</script>

<template>
  <div @create="onCrudCreate" @delete="onCrudDelete">
    <router-view />
  </div>
</template>

<script>
import FooterComponent from "./components/FooterComponent.vue";
import HeaderComponent from "./components/HeaderComponent.vue";

export default {
  components: {
    HeaderComponent,
    FooterComponent,
  },
};
</script>

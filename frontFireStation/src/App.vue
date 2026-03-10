<template>
  <div @create="onCrudCreate" @delete="onCrudDelete">
    <router-view />
    <CrudPanel 
      @create="handleCreate"
      @delete="handleDelete"
    />
  </div>
</template>

<script>
import FooterComponent from "./components/FooterComponent.vue";
import HeaderComponent from "./components/HeaderComponent.vue";
import CrudPanel from "./components/CrudPanel.vue";

export default {
  components: {
    HeaderComponent,
    FooterComponent,
    CrudPanel,
  },
  methods: {
    handleCreate() {
      // Отправляем событие на активную страницу через window
      window.dispatchEvent(new CustomEvent('crud:create'));
    },
    handleDelete() {
      // Отправляем событие на активную страницу через window
      window.dispatchEvent(new CustomEvent('crud:delete'));
    },
  },
};
</script>

<template>
  <div @create="onCrudCreate" @delete="onCrudDelete">
    <router-view />
  </div>
</template>

<script>


export default {
  components: {

  },
};
</script>

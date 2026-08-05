<script setup>
import { useAuth } from '@/stores/auth';

const auth = useAuth()

</script>

<template>
<div class="login-page">
    <BCard >
      <h2 class="text-center fw-bold text-uppercase mb-1">Logged In</h2>
      <p>you are {{ auth.userName}} : {{auth.role}}</p>
    </BCard>
</div>
</template>

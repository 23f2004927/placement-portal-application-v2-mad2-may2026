<script setup>
import { login } from '@/services/auth';
import { useAuth } from '@/stores/auth';
import { ref } from 'vue';
import { RouterLink, useRouter } from 'vue-router';


const username = ref('') // input from form
const password = ref('') // input from form
const errorMsg = ref('')

const router = useRouter()   // must be called at setup top level, not inside the function

async function handleSubmit() {
  errorMsg.value = ''
  const auth = useAuth()
  try {
    console.log('would log in with', username.value, password.value)
    const data = await login(username.value, password.value)   // { access_token, role }
    auth.setSession(data.access_token, data.role,data.userName)
     router.push('/logged')
  } catch (err) {

    errorMsg.value = 'Invalid username or password'
    console.log(err)
  }
}

</script>

<template>
<div class="login-page">
    <BCard class="login-card">

      <h2 class="text-center fw-bold text-uppercase mb-1">Portal Login</h2>
      <p class="text-center subtitle mb-4">Please sign in to access your account.</p>

      <BForm @submit.prevent="handleSubmit">

        <BAlert v-if="errorMsg" variant="danger">{{ errorMsg }}</BAlert>

        <BFormFloatingLabel label="Username" label-for="username" class="my-2">
          <BFormInput id="username" type="text" v-model="username" placeholder="Username"  required/>
        </BFormFloatingLabel>

        <BFormGroup>
          <BFormFloatingLabel label="Password" label-for="floatingPassword" class="my-2">

          <BFormInput v-model="password" id="floatingPassword" placeholder="Password" type="password" required/>
          </BFormFloatingLabel>

          <RouterLink to="/forgot-password" class="forgot-link">Forgot Password?</RouterLink>
        </BFormGroup>

        <BButton type="submit" variant="primary">Login</BButton>

        <p class="text-center subtitle signup-row mb-0">
          Don't have an account?
          <RouterLink to="/register/student" class="signup-link">Student</RouterLink>
          |
          <RouterLink to="/register/company" class="signup-link">Company</RouterLink>
        </p>

      </BForm>
    </BCard>
</div>
</template>


<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--bg);
}

.login-card{
    width:420px;
    padding:48px;
}

.form-group{
    margin-bottom:24px;
}
</style>

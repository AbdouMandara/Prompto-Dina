<template>
  <div class="welcome-page">
    <div class="container">
      <span class="eyebrow">Prompto~Dina</span>
      <h1>Construisez un prompt IA puissant</h1>
      <p>Étape par étape, générez des prompts clairs et optimisés</p>
      <router-link to="/prompt_view" class="cta-button">Commencer</router-link>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.welcome-page {
  min-height: 100vh;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  /* background: linear-gradient(135deg, #f8fafb 0%, #eef6f9 100%); */
  font-family: 'Poppins', sans-serif;
}

.container {
  text-align: center;
  max-width: 600px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.eyebrow {
  display: inline-block;
  padding: 0.5rem 1rem;
  background: #e8f5f1;
  color: #0f8b74;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  width: fit-content;
  margin: 0 auto;
}

.container h1 {
  font-size: clamp(2rem, 5vw, 3.2rem);
  line-height: 1.1;
  letter-spacing: -0.02em;
  color: #1a202c;
  font-weight: 700;
}

.container p {
  font-size: 1.05rem;
  color: #5a6c7d;
  line-height: 1.6;
}

.cta-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #0f8b74, #0d7a66);
  color: white;
  font-weight: 700;
  font-size: 1rem;
  text-decoration: none;
  border-radius: 12px;
  transition: all 0.3s ease;
  box-shadow: 0 8px 20px rgba(15, 139, 116, 0.2);
}

@media (max-width: 640px) {
  .container {
    padding: 1.5rem;
    gap: 1.25rem;
  }

  .container h1 {
    font-size: 1.8rem;
  }

  .container p {
    font-size: 0.95rem;
  }

  .cta-button {
    padding: 0.9rem 1.8rem;
    font-size: 0.95rem;
  }
}
</style>

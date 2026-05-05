<template>
  <section class="wizard">
    <div class="wizard-container">
      <div class="wizard-card">
        <div class="progress-bar-container">
          <div class="progress-bar-track">
            <div class="progress-bar-fill" :style="{ width: progressPercentage + '%' }"></div>
          </div>
          <div class="progress-labels">
            <div class="step-indicator">
              <span class="step-counter">Étape {{ stepIndex + 1 }} / {{ steps.length }}</span>
              <span class="step-name">{{ currentStep.shortLabel }}</span>
            </div>
            <div class="backend-status">{{ backendStatus }}</div>
          </div>
        </div>
        <div class="step-content">
          <h2>{{ currentStep.title }}</h2>
          <p v-if="currentStep.description" class="subtitle">{{ currentStep.description }}</p>

          <template v-if="currentStep.type === 'textarea'">
            <label :for="currentStep.key">{{ currentStep.label }}</label>
            <textarea
              :id="currentStep.key"
              v-model="formData[currentStep.key]"
              :placeholder="currentStep.placeholder"
              rows="5"
              spellcheck="true"
              :aria-label="currentStep.label"
            />
          </template>

          <template v-else-if="currentStep.type === 'select'">
            <div class="options-grid">
              <button
                v-for="option in currentStep.options"
                :key="option"
                type="button"
                :class="['pill', { selected: formData[currentStep.key] === option }]"
                @click="selectOption(currentStep.key, option)"
              >
                {{ option }}
              </button>
            </div>
          </template>

          <template v-else-if="currentStep.type === 'text'">
            <label :for="currentStep.key">{{ currentStep.label }}</label>
            <input
              :id="currentStep.key"
              v-model="formData[currentStep.key]"
              :placeholder="currentStep.placeholder"
              type="text"
              :aria-label="currentStep.label"
            />
          </template>
        </div>

        <div class="wizard-actions">
          <button type="button" class="secondary" @click="prevStep" :disabled="stepIndex === 0 || loading">Retour</button>
          <div class="actions-right">
            <button
              v-if="generatedPrompt"
              type="button"
              class="tertiary"
              @click="editPromptConfig"
              :disabled="loading"
            >
              Modifier la configuration
            </button>
            <button
              type="button"
              class="primary"
              @click="nextOrGenerate"
              :disabled="!isStepValid(currentStep) || loading"
            >
              <span v-if="loading">Chargement...</span>
              <span v-else>{{ stepIndex < steps.length - 1 ? 'Suivant' : generatedPrompt ? 'Mettre à jour le prompt' : 'Générer le prompt' }}</span>
            </button>
          </div>
        </div>

        <div v-if="error" class="notification error" role="alert">{{ error }}</div>
        <div v-if="suggestions.length && !generatedPrompt" class="suggestions">
          <strong>Suggestions automatiques :</strong>
          <ul>
            <li v-for="suggestion in suggestions" :key="suggestion">{{ suggestion }}</li>
          </ul>
        </div>
      </div>

      <section v-if="generatedPrompt" class="result-panel">
        <div class="result-card">
          <div class="result-card-header">
            <div>
              <h3>Prompt généré</h3>
              <p class="small-text">Vous pouvez copier, personnaliser ou améliorer ce prompt.</p>
            </div>
            <button type="button" class="secondary" @click="copyPrompt">Copier</button>
          </div>
          <pre>{{ generatedPrompt }}</pre>
        </div>

        <div class="result-card actions">
          <h3>Actions rapides</h3>
          <div class="action-buttons">
            <button type="button" @click="refinePrompt('simplifier')">Simplifier</button>
            <button type="button" @click="refinePrompt('detaille')">Détailler</button>
            <button type="button" @click="refinePrompt('technique')">Plus technique</button>
            <button type="button" @click="refinePrompt('professionnel')">Changer le ton</button>
          </div>
        </div>

        <div class="result-card">
          <div class="result-card-header">
            <div>
              <h3>Tester avec un provider IA</h3>
              <p class="small-text">Sélectionnez le provider et lancez un test en direct.</p>
            </div>
            <button type="button" class="secondary" @click="clearAIResponse" :disabled="loading">Effacer</button>
          </div>

          <button type="button" class="primary" @click="testPrompt" :disabled="loading" style="width: 100%; max-width: 400px;">
            {{ loading ? 'En cours...' : 'Tester avec HuggingFace' }}
          </button>

          <div v-if="aiResponse" class="ai-response">
            <div class="ai-response-header">
              <h4>Réponse IA</h4>
              <button type="button" class="secondary" @click="copyAIResponse" :disabled="loading">Copier</button>
            </div>
            <pre>{{ aiResponse }}</pre>
          </div>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'

const apiBase = import.meta.env.VITE_API_BASE_URL
const formData = reactive({
  idea: '',
  objective: '',
  role: '',
  level: '',
  responseFormat: '',
  tone: '',
  length: '',
  constraints: '',
})

const stepIndex = ref(0)
const loading = ref(false)
const generatedPrompt = ref('')
const aiResponse = ref('')
const error = ref('')
const suggestions = ref([])
const backendStatus = ref('Recherche du backend...')

const progressPercentage = computed(() => {
  return ((stepIndex.value + 1) / steps.length) * 100
})

const steps = [
  {
    key: 'idea',
    title: 'Décrivez votre idée',
    shortLabel: 'Idée',
    label: 'Votre idée',
    description: 'Entrez la base de votre demande, même si elle est encore floue.',
    type: 'textarea',
    placeholder: 'Exemple : créer un plan de contenu pour un blog de productivité',
  },
  {
    key: 'objective',
    title: 'Définissez l’objectif',
    shortLabel: 'Objectif',
    label: 'Objectif de l’IA',
    description: 'Choisissez le résultat principal que vous attendez.',
    type: 'select',
    options: ['apprendre', 'créer', 'analyser', 'résoudre'],
  },
  {
    key: 'role',
    title: 'Choisissez le rôle de l’IA',
    shortLabel: 'Rôle',
    label: 'Rôle de l’IA',
    description: 'Sélectionnez le style de l’IA pour ce prompt.',
    type: 'select',
    options: ['professeur', 'développeur', 'expert', 'coach'],
  },
  {
    key: 'level',
    title: 'Votre niveau',
    shortLabel: 'Niveau',
    label: 'Niveau utilisateur',
    description: 'Aidez l’IA à adapter la réponse à votre niveau.',
    type: 'select',
    options: ['débutant', 'intermédiaire', 'avancé'],
  },
  {
    key: 'responseFormat',
    title: 'Format de réponse souhaité',
    shortLabel: 'Format',
    label: 'Format attendu',
    description: 'Choisissez le format le plus utile pour votre usage.',
    type: 'select',
    options: ['étapes', 'code', 'explication', 'tableau', 'JSON'],
  },
  {
    key: 'tone',
    title: 'Choisissez le ton',
    shortLabel: 'Ton',
    label: 'Ton',
    description: 'Définissez l’ambiance de la réponse.',
    type: 'select',
    options: ['simple', 'professionnel', 'technique'],
  },
  {
    key: 'length',
    title: 'Choisissez la longueur',
    shortLabel: 'Longueur',
    label: 'Longueur',
    description: 'Court, moyen ou détaillé : adaptez selon votre besoin.',
    type: 'select',
    options: ['court', 'moyen', 'détaillé'],
  },
  {
    key: 'constraints',
    title: 'Contraintes avancées',
    shortLabel: 'Contraintes',
    label: 'Contraintes avancées',
    description: 'Langue, structure, limite de mots, style ou restrictions spécifiques.',
    type: 'textarea',
    placeholder: 'Exemple : Répondre en français, utiliser des bullet points, ne pas dépasser 120 mots',
  },
]

const currentStep = computed(() => steps[stepIndex.value])

onMounted(() => {
  checkBackendConnection()
})

function selectOption(key, option) {
  formData[key] = option
}

function isStepValid(step) {
  const value = formData[step.key]
  return typeof value === 'string' && value.trim().length > 0
}

function prevStep() {
  error.value = ''
  if (stepIndex.value > 0) stepIndex.value -= 1
}

function jumpToStep(index) {
  if (index <= stepIndex.value && !loading.value) {
    stepIndex.value = index
  }
}

function editPromptConfig() {
  generatedPrompt.value = ''
  aiResponse.value = ''
  stepIndex.value = 0
}

async function checkBackendConnection() {
  backendStatus.value = 'Connexion en cours...'
  try {
    const response = await fetch(`${apiBase}/ping`)
    if (!response.ok) {
      throw new Error('Backend indisponible')
    }

    const data = await response.json()
    backendStatus.value = data.status === 'ok' ? 'Backend prêt' : 'Backend répondu'
  } catch (err) {
    backendStatus.value = 'Impossible de joindre le backend'
  }
}

function clearAIResponse() {
  aiResponse.value = ''
}

function copyPrompt() {
  navigator.clipboard.writeText(generatedPrompt.value).catch(() => {
    error.value = 'Impossible de copier le prompt pour le moment.'
  })
}

function copyAIResponse() {
  navigator.clipboard.writeText(aiResponse.value).catch(() => {
    error.value = 'Impossible de copier la réponse IA pour le moment.'
  })
}

async function nextOrGenerate() {
  error.value = ''
  if (!isStepValid(currentStep.value)) {
    error.value = 'Veuillez répondre à cette étape avant de continuer.'
    return
  }

  if (stepIndex.value < steps.length - 1) {
    stepIndex.value += 1
    return
  }

  await generatePrompt()
}

async function generatePrompt() {
  loading.value = true
  aiResponse.value = ''
  generatedPrompt.value = ''
  suggestions.value = []

  try {
    const response = await fetch(`${apiBase}/generate_prompt`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    })

    if (!response.ok) {
      throw new Error('Erreur lors de la génération du prompt')
    }

    const data = await response.json()
    generatedPrompt.value = data.prompt
    suggestions.value = data.suggestions || []
    stepIndex.value = steps.length - 1
  } catch (err) {
    error.value = err.message || 'Échec de la communication avec le back-end.'
  } finally {
    loading.value = false
  }
}

async function testPrompt() {
  if (!generatedPrompt.value) {
    error.value = 'Générez d’abord un prompt avant de le tester.'
    return
  }

  loading.value = true
  error.value = ''
  aiResponse.value = ''

  try {
    const response = await fetch(`${apiBase}/test_prompt`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: generatedPrompt.value }),
    })

    if (!response.ok) {
      throw new Error('Erreur lors de l’appel IA')
    }

    const data = await response.json()
    aiResponse.value = data.response
  } catch (err) {
    error.value = err.message || 'Impossible de récupérer la réponse IA.'
  } finally {
    loading.value = false
  }
}

async function refinePrompt(action) {
  if (!generatedPrompt.value) return
  loading.value = true
  error.value = ''

  try {
    const response = await fetch(`${apiBase}/refine_prompt`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: generatedPrompt.value, action }),
    })

    if (!response.ok) {
      throw new Error('Erreur lors de l’amélioration du prompt')
    }

    const data = await response.json()
    generatedPrompt.value = data.prompt
  } catch (err) {
    error.value = err.message || 'Impossible d’améliorer le prompt.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --accent: #0f8b74;
  --accent-dark: #0d7a66;
  --accent-light: #e8f5f1;
  --text: #1a202c;
  --text-muted: #5a6c7d;
  --bg-light: #f8fafb;
  --bg-subtle: #eef6f9;
  --border: #d1d5db;
}

.wizard {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafb 0%, #eef6f9 100%);
  padding: 0 1rem 2rem;
  font-family: 'Poppins', sans-serif;
  display: flex;
  flex-direction: column;
}

.wizard-container {
  width: min(100%, 900px);
  margin: 0 auto;
  margin-top: 2rem;
}

.wizard-card,
.result-panel {
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: 20px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  padding: 2.5rem;
  margin-bottom: 1.5rem;
}

.step-content {
  margin-bottom: 2rem;
}

.step-content h2 {
  font-size: 1.75rem;
  margin-bottom: 0.5rem;
  color: #1a202c;
  font-weight: 700;
}

.step-content .subtitle {
  color: #5a6c7d;
  font-size: 1rem;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.step-content label {
  display: block;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: #1a202c;
  font-size: 0.95rem;
}

textarea,
input,
select {
  width: 100%;
  padding: 0.95rem 1rem;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: #ffffff;
  font-size: 0.95rem;
  color: #1a202c;
  font-family: 'Poppins', sans-serif;
  resize: vertical;
  transition: border-color 0.2s, box-shadow 0.2s;
  outline: none;
}

textarea:focus,
input:focus,
select:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(15, 139, 116, 0.1);
  background: white;
}

.options-grid {
  display: grid;
  gap: 0.8rem;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  margin-top: 1rem;
}

.pill {
  border: 1px solid var(--border);
  background: #ffffff;
  color: #1a202c;
  padding: 0.9rem 1rem;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
  min-height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  font-family: 'Poppins', sans-serif;
}

.pill:hover {
  border-color: var(--accent);
  background: var(--accent-light);
  transform: translateY(-1px);
}

.pill.selected {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
}

.wizard-actions {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  margin-top: 2rem;
}

.actions-right {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

button {
  appearance: none;
  border: 0;
  border-radius: 12px;
  padding: 0.95rem 1.5rem;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Poppins', sans-serif;
}

button.primary {
  background: linear-gradient(135deg, #0f8b74, #0d7a66);
  color: white;
  box-shadow: 0 8px 20px rgba(15, 139, 116, 0.2);
}

button.primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(15, 139, 116, 0.3);
}

button.secondary,
button.tertiary {
  background: #ffffff;
  color: #1a202c;
  border: 1px solid var(--border);
}

button.secondary:hover:not(:disabled),
button.tertiary:hover:not(:disabled) {
  border-color: var(--accent);
  background: var(--accent-light);
  transform: translateY(-1px);
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.notification.error {
  margin-top: 1rem;
  padding: 1rem;
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 12px;
  color: #991b1b;
  font-weight: 600;
}

.suggestions {
  margin-top: 1.5rem;
  padding: 1.25rem;
  background: var(--accent-light);
  border-radius: 12px;
  border: 1px solid rgba(15, 139, 116, 0.2);
}

.suggestions strong {
  display: block;
  margin-bottom: 0.75rem;
  color: var(--accent);
}

.suggestions ul {
  list-style: none;
  padding: 0;
}

.suggestions li {
  color: var(--text-muted);
  padding: 0.4rem 0;
  font-size: 0.95rem;
}

.result-card {
  padding: 1.5rem;
  border: 1px solid var(--border);
  border-radius: 16px;
  background: #ffffff;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
}

.result-card h3,
.result-card h4 {
  margin: 0 0 0.5rem;
  color: #1a202c;
}

.result-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.result-card-header .small-text {
  margin: 0.25rem 0 0;
  color: #5a6c7d;
  font-size: 0.9rem;
}

.result-card pre {
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
  background: #f8fafb;
  border-radius: 12px;
  padding: 1rem;
  border: 1px solid var(--border);
  color: #1a202c;
  font-size: 0.9rem;
  overflow-x: auto;
}

.action-buttons {
  display: grid;
  gap: 0.8rem;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
}

.action-buttons button {
  background: #ffffff;
  color: #1a202c;
  border: 1px solid var(--border);
}

.ai-response {
  margin-top: 1rem;
}

.ai-response-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.progress-bar-container {
  margin: -2.5rem -2.5rem 2rem -2.5rem;
  background: white;
  border-bottom: 1px solid var(--border);
  padding: 1.5rem 2.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.progress-bar-track {
  width: 100%;
  height: 8px;
  background: #d1d5db;
  border-radius: 999px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #0f8b74, #0d7a66);
  border-radius: 999px;
  transition: width 0.3s ease;
}

.progress-labels {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  max-width: 900px;
  margin: 0 auto;
}

.step-indicator {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.step-counter {
  font-size: 0.85rem;
  color: #5a6c7d;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.step-name {
  font-size: 1.1rem;
  color: #1a202c;
  font-weight: 700;
}

.backend-status {
  padding: 0.5rem 1rem;
  border-radius: 999px;
  background: #e8f5f1;
  color: #0f8b74;
  font-size: 0.9rem;
  font-weight: 500;
  border: 1px solid rgba(15, 139, 116, 0.2);
}

@media (max-width: 768px) {
  .wizard {
    padding: 1.5rem 1rem;
  }

  .wizard-container {
    margin-top: 1rem;
  }

  .progress-bar-container {
    margin: -1.5rem -1.5rem 1rem -1.5rem;
    padding: 1.25rem 1.5rem;
  }

  .wizard-card,
  .result-panel {
    padding: 1.5rem;
  }

  .step-content h2 {
    font-size: 1.4rem;
  }

  .options-grid {
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  }

  .wizard-actions,
  .actions-right,
  .result-card-header {
    flex-direction: column;
    align-items: stretch;
  }

  .progress-labels {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 640px) {
  .wizard-card,
  .result-panel {
    padding: 1.25rem;
  }

  .progress-bar-container {
    padding: 1rem;
  }

  button {
    padding: 0.85rem 1.25rem;
    font-size: 0.9rem;
  }

  .action-buttons {
    grid-template-columns: 1fr;
  }
}
</style>

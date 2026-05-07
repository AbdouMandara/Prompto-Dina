<template>
  <section class="wizard">
    <div class="wizard-container">
      <div v-if="!promptGenerated" class="wizard-card">
        <div class="progress-bar-container">
          <div class="progress-bar-track">
            <div class="progress-bar-fill" :style="{ width: progressPercentage + '%' }"></div>
          </div>
          <div class="progress-labels">
            <div class="step-indicator">
              <span class="step-name">{{ currentStep.shortLabel }}</span>
            </div> 
          </div>
        </div>
        <div class="step-content">
          <p v-if="currentStep.description" class="subtitle">{{ currentStep.description }}</p>

          <template v-if="currentStep.type === 'textarea'">
            <label :for="currentStep.key"></label>
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
            <div class="options-grid" :class="{ 'two-columns': currentStep.key === 'tone' }">
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
            <div v-if="currentStepCustomOptions.length" class="custom-options">
              <strong>Vos propositions :</strong>
              <div class="options-grid">
                <button
                  v-for="option in currentStepCustomOptions"
                  :key="option"
                  type="button"
                  :class="['pill', 'custom', { selected: formData[currentStep.key] === option }]"
                  @click="selectOption(currentStep.key, option)"
                >
                  {{ option }}
                </button>
              </div>
            </div>
            <div v-if="stepIndex > 0" class="add-custom-option">
              <button type="button" class="add-btn" @click="showCustomOptionForm = !showCustomOptionForm">
                {{ showCustomOptionForm ? '✕ Annuler' : '+ Ajouter une proposition' }}
              </button>
              <div v-if="showCustomOptionForm" class="form-add-option">
                <input
                  v-model="newCustomOption"
                  type="text"
                  placeholder="Entrez votre proposition"
                  @keyup.enter="addNewCustomOption"
                />
                <button type="button" class="secondary" @click="addNewCustomOption" :disabled="!newCustomOption.trim()">
                  Ajouter
                </button>
              </div>
            </div>
          </template>

          <template v-else-if="currentStep.type === 'text'">
            <!-- <label :for="currentStep.key">{{ currentStep.label }}</label> -->
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
        <div v-if="stepIndex === 0 && ideaSuggestions.length" class="suggestions">
          <strong>Suggestions basées sur votre idée :</strong>
          <div class="suggestion-buttons">
            <button
              v-for="suggestion in ideaSuggestions"
              :key="suggestion"
              type="button"
              class="suggestion-btn"
              @click="applySuggestion(suggestion)"
            >
              {{ suggestion }}
            </button>
          </div>
        </div>
        <div v-if="suggestions.length && !generatedPrompt" class="suggestions">
          <strong>Suggestions automatiques :</strong>
          <ul>
            <li v-for="suggestion in suggestions" :key="suggestion">{{ suggestion }}</li>
          </ul>
        </div>
      </div>

      <section v-if="generatedPrompt || aiResponse" class="result-panel">
        <div class="result-panel-header">
          <button type="button" class="tertiary" @click="editPromptConfig" :disabled="loading">
            ← Modifier la configuration
          </button>
          <button type="button" class="primary" @click="testPrompt" :disabled="loading">
            {{ loading ? 'Prompt en cours de génération' : aiResponse ? 'Régénérer à nouveau' : "Améliorer avec l'IA" }}
          </button>
        </div>
        <div v-if="!generatedPrompt" class="result-card">
          <div class="result-card-header">
            <div>
              <h3>Résumé de votre demande</h3>
              <p class="small-text">Voici un aperçu de vos paramètres. Confirmez pour générer votre prompt.</p>
            </div>
          </div>
          <div class="summary-content">
            <div class="summary-item"><strong>Idée :</strong> {{ formData.idea }}</div>
            <div class="summary-item"><strong>Objectif :</strong> {{ formData.objective }}</div>
            <div class="summary-item"><strong>Rôle :</strong> {{ formData.role }}</div>
            <div class="summary-item"><strong>Niveau :</strong> {{ formData.level }}</div>
            <div class="summary-item"><strong>Format :</strong> {{ formData.responseFormat }}</div>
            <div class="summary-item"><strong>Ton :</strong> {{ formData.tone }}</div>
            <div class="summary-item"><strong>Longueur :</strong> {{ formData.length }}</div>
            <div class="summary-item"><strong>Contraintes :</strong> {{ formData.constraints || 'Aucune' }}</div>
          </div>
          <div style="margin-top: 1.5rem; display: flex; gap: 0.75rem;">
            <button type="button" class="primary" @click="generatePrompt" :disabled="loading">
              {{ loading ? 'Génération...' : 'Générer le prompt' }}
            </button>
          </div>
        </div>

        <div v-if="generatedPrompt && !aiResponse" class="result-card">
          <div class="result-card-header">
            <div>
              <h3>Résumé de votre demande</h3>
              <p class="small-text">Voici un résumé de vos paramètres. Confirmez pour générer votre prompt.</p>
            </div>
            <button type="button" class="secondary copy-button" @click="copyPrompt">
              <span class="copy-icon">📋</span>
              <span>{{ copiedPrompt ? 'Copié' : 'Copier' }}</span>
            </button>
          </div>
          <pre>{{ generatedPrompt }}</pre>
        </div>

        <div v-if="generatedPrompt && !aiResponse" class="result-card actions">
          <h3>Actions rapides</h3>
          <div class="action-buttons">
            <button type="button" @click="refinePrompt('simplifier')">Simplifier</button>
            <button type="button" @click="refinePrompt('detaille')">Détailler</button>
            <button type="button" @click="refinePrompt('technique')">Plus technique</button>
            <button type="button" @click="refinePrompt('professionnel')">Changer le ton</button>
          </div>
        </div>

        <div v-if="aiResponse" class="result-card">
          <div class="result-card-header">
            <div>
              <h3>Réponse IA</h3>
              <p class="small-text">Voici la réponse générée par l'IA basée sur votre prompt.</p>
            </div>
            <button type="button" class="secondary copy-button" @click="copyAIResponse" :disabled="loading">
              <span class="copy-icon">📋</span>
              <span>{{ copiedAIResponse ? 'Copié' : 'Copier' }}</span>
            </button>
          </div>
          <pre>{{ aiResponse }}</pre>
        </div>

        <div v-if="error" class="result-card error-card">
          <div class="result-card-header">
            <div>
              <h3>Erreur</h3>
              <p class="small-text">Une erreur est survenue.</p>
            </div>
            <button type="button" class="secondary copy-button" @click="error = ''">
              <span>✕ Fermer</span>
            </button>
          </div>
          <div class="error-message">{{ error }}</div>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup>
import { reactive, ref, computed, onMounted, watch } from 'vue'
import { useCustomOptionsStore } from '../stores/customOptions'

const apiBase = import.meta.env.VITE_API_BASE_URL
const customOptionsStore = useCustomOptionsStore()
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
const ideaSuggestions = ref([])
const newCustomOption = ref('')
const showCustomOptionForm = ref(false)
const promptGenerated = ref(false)
const copiedPrompt = ref(false)
const copiedAIResponse = ref(false)

const progressPercentage = computed(() => {
  return ((stepIndex.value + 1) / steps.length) * 100
})

const steps = [
  {
    key: 'idea',
    title: 'Décrivez votre idée',
    shortLabel: 'Idée',
    label: 'Votre idée',
    description: 'Entrez votre demande, même si elle est encore floue.',
    type: 'textarea',
    placeholder: 'Exemple : Apprendre le Python',
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
    options: ['simple', 'professionnel', 'technique', 'educatif'],
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

// Générer les suggestions basées sur l'idée et l'objectif
function generateIdeaSuggestions() {
  const idea = formData.idea.trim().toLowerCase()
  if (idea.length < 2) {
    ideaSuggestions.value = []
    return
  }

  const objectiveOptions = ['apprendre', 'créer', 'analyser', 'résoudre']
  ideaSuggestions.value = objectiveOptions.map(obj => {
    return `${obj} ${idea}`
  })
}

// Surveiller les changements de l'idée
watch(() => formData.idea, () => {
  generateIdeaSuggestions()
})

// Charger les options personnalisées pour l'étape actuelle
const currentStepCustomOptions = computed(() => {
  return customOptionsStore.getCustomOptions(currentStep.value.key) || []
})

// Ajouter une option personnalisée
function addNewCustomOption() {
  const option = newCustomOption.value.trim()
  if (option && !currentStepCustomOptions.value.includes(option)) {
    customOptionsStore.addCustomOption(currentStep.value.key, option)
    newCustomOption.value = ''
  }
}

// Appliquer une suggestion à l'idée
function applySuggestion(suggestion) {
  formData.idea = suggestion
}

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
  promptGenerated.value = false
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
  navigator.clipboard.writeText(generatedPrompt.value)
    .then(() => {
      copiedPrompt.value = true
      setTimeout(() => {
        copiedPrompt.value = false
      }, 1500)
    })
    .catch(() => {
      error.value = 'Impossible de copier le prompt pour le moment.'
    })
}

function copyAIResponse() {
  navigator.clipboard.writeText(aiResponse.value)
    .then(() => {
      copiedAIResponse.value = true
      setTimeout(() => {
        copiedAIResponse.value = false
      }, 1500)
    })
    .catch(() => {
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
    promptGenerated.value = true
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
  min-height: max-content;
  background: #ffffff;
  padding: 0 1rem 2rem;
  font-family: 'Poppins', sans-serif;
  display: flex;
  flex-direction: column;
}

.wizard-container {
  min-width : 600px;
  max-width: 900px;
  margin: 0 auto;
  margin-top: 2rem;
}

.wizard-card,
.result-panel {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  background: #ffffff;
  /* border: 1px solid #d1d5db; */
  border-radius: 20px;
  /* box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08); */
  padding: 2.5rem;
  margin-bottom: 1.5rem;
}

.result-panel {
  position: relative;
}

.step-content,
.step-content > * {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.step-content textarea,
.step-content input,
.step-content select {
  width: 100%;
  max-width: 100%;
  display: block;
}

.result-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
  flex-wrap: wrap;
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
  border: 1px solid #d1d5db;
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
  /* border-color: var(--accent); */
  box-shadow: 0 0 0 3px rgba(15, 139, 116, 0.1);
  background: white;
}

.options-grid {
  display: grid;
  gap: 0.8rem;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  margin-top: 1rem;
}

.options-grid.two-columns {
  grid-template-columns: repeat(2, 1fr);
}

.pill {
  border: 1px solid #d1d5db;
  background: #ffffff;
  color: #1a202c;
  padding: 0.35rem 0.5rem;
  border-radius: 999px;
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
  border-color: #0f8b74;
  background: #e8f5f1;
}

.pill.selected {
  padding: 0.35rem 0.5rem;
  border-radius: 999px;
  background: #e8f5f1;
  color: #0f8b74;
  font-size: 0.9rem;
  font-weight: 500;
  border: 1px solid rgba(15, 139, 116, 0.2);
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
  border-radius: 8px;
  padding: 0.5rem 1.5rem;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Poppins', sans-serif;
}

button.primary {
  background: linear-gradient(135deg, #0f8b74, #0d7a66);
  color: white;
}

button.secondary,
button.tertiary {
  background: #ffffff;
  color: #1a202c;
  border: 1px solid #d1d5db;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

button.secondary:hover:not(:disabled),
button.tertiary:hover:not(:disabled) {
  border-color: #0f8b74;
  background: #e8f5f1;
  
}

.copy-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.copy-icon {
  font-size: 1rem;
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

.suggestion-buttons {

  flex-direction: column;
  display: flex;
  align-items: start;
  gap: 0.5rem;
  margin-top: 1rem;
}

.suggestion-btn {
  background: white;
  color: black;
  border: 1px solid var(--accent);
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Poppins', sans-serif;
}

.suggestion-btn:hover {
  background: var(--accent-light);
  border-color: var(--accent);
}

.custom-options {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border);
}

.custom-options strong {
  display: block;
  margin-bottom: 0.75rem;
  color: #1a202c;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.pill.custom {
  background: var(--accent-light);
  color: var(--accent);
}

.pill.custom:hover {
  background: var(--accent);
  color: white;
}

.add-custom-option {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border);
}

.add-btn {
  background: #ffffff;
  color: #0f8b74;
  border: 1px dashed #0f8b74;
  padding: 0.75rem 1rem;
  font-size: 0.9rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: 'Poppins', sans-serif;
  font-weight: 600;
}

.add-btn:hover {
  background: var(--accent-light);
  border-style: solid;
}

.form-add-option {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
  flex-wrap: wrap;
}

.form-add-option input {
  flex: 1;
  min-width: 200px;
  padding: 0.75rem 1rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: #f8fafb;
  color: #1a202c;
  font-family: 'Poppins', sans-serif;
  font-size: 0.9rem;
}

.form-add-option input:focus {
  outline: none;
  border-color: var(--accent);
  background: white;
  box-shadow: 0 0 0 3px rgba(15, 139, 116, 0.1);
}

.form-add-option button {
  padding: 0.75rem 1.5rem;
  font-size: 0.9rem;
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

.summary-content {
  display: grid;
  gap: 1rem;
  padding: 1rem;
  background: #f8fafb;
  border-radius: 12px;
  border: 1px solid var(--border);
}

.summary-item {
  padding: 0.75rem;
  background: white;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  font-size: 0.9rem;
  color: #1a202c;
  line-height: 1.5;
}

.summary-item strong {
  color: #0f8b74;
  font-weight: 600;
  display: inline-block;
  min-width: 100px;
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

.error-card {
  position: absolute;
  left: 1.5rem;
  bottom: 1.5rem;
  width: calc(100% - 3rem);
  max-width: 420px;
  border: 2px solid #dc2626;
  background: #fef2f2;
  z-index: 10;
}

.error-card h3 {
  color: #dc2626;
}

.error-message {
  padding: 1rem;
  background: #fee2e2;
  border-radius: 12px;
  color: #991b1b;
  font-weight: 500;
  line-height: 1.6;
}

.progress-bar-container {
  margin: -2.5rem -2.5rem 0.5rem -2.5rem;
  border-bottom: 0.65px solid #0000001f;
  background: white;
  border-bottom: 1px solid var(--border);
  padding: 1.5rem 2.5rem;
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
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
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
  font-size: 1.5rem;
  color: #1a202c;
  font-weight: 700;
  text-align: center;
}

/* .backend-status {
  padding: 0.5rem 1rem;
  border-radius: 999px;
  background: #e8f5f1;
  color: #0f8b74;
  font-size: 0.9rem;
  font-weight: 500;
  border: 1px solid rgba(15, 139, 116, 0.2);
} */

@media (max-width: 768px) {
  .wizard {
    padding: 1.5rem 1rem;
  }

  .wizard-container {
    margin-top: 1rem;
  }

  .progress-bar-container {
    padding: 1.25rem 1.5rem;
    margin: -1.5rem -1.25rem 1rem -1.25rem;
    border-bottom: 0.65px solid #0000001f;
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

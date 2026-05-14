<template>
  <div class="app-wrapper">
    <header class="app-header">
      <h1 class="app-name">Prompto~Dina</h1>
    </header>
    
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
              <button
                v-for="option in currentStepCustomOptions"
                :key="option"
                type="button"
                :class="['pill', { selected: formData[currentStep.key] === option }]"
                @click="selectOption(currentStep.key, option)"
              >
                {{ option }}
              </button>
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
      </div>

      <section v-if="generatedPrompt || aiResponse" class="result-panel">
        <div class="result-panel-header">
          <button type="button" class="tertiary" @click="editPromptConfig" :disabled="loading">
            <span class="mobile-hidden">← </span><span class="mobile-text">←</span><span class="mobile-hidden"> Modifier la configuration</span>
          </button>
          <button type="button" class="primary" @click="testPrompt" :disabled="loading">
            {{ loading ? 'Prompt en cours de génération' : aiResponse ? 'Régénérer à nouveau' : "Avoir le prompt" }}
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
              <p class="small-text">Voici un résumé de vos paramètres.</p>
            </div>
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
              <p class="small-text">Voici le prompt générée par l'IA basée sur vos infos.</p>
            </div>
            <button type="button" class="secondary copy-button" @click="copyAIResponse" :disabled="loading">
              <span class="copy-icon">📋</span>
              <span>{{ copiedAIResponse ? 'Copié' : 'Copier' }}</span>
            </button>
          </div>
          <pre>{{ aiResponse }}</pre>
        </div>
      </section>
      <div v-if="error" class="result-card error-card">
        <div class="result-card-header">
          <div>
            <!-- <h3>Erreur</h3> -->
            <p class="small-text-error">Une erreur est survenue.</p>
          </div>
        </div>
        <!-- <div class="error-message">{{ error }}</div> -->
      </div>
    </div>
    </section>

    <footer class="app-footer">
      <div class="footer-content">
        <p>Fait par <strong>Abdou Mandara</strong></p>
        <div class="social-links">
          <a href="https://linkedin.com/in/abdou-mandara" target="_blank" rel="noopener" title="LinkedIn" class="social-link">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M16 8a6 6 0 016 6v7h-4v-7a2 2 0 00-2-2 2 2 0 00-2 2v7h-4v-7a6 6 0 016-6zM2 9h4v12H2z"></path>
              <circle cx="4" cy="4" r="2"></circle>
            </svg>
          </a>
          <a href="https://tiktok.com/@its_abdou_mandara" target="_blank" rel="noopener" title="TikTok" class="social-link">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 12a4 4 0 1 0 4 4V4a5 5 0 0 0 5 5"></path>
            </svg>
          </a>
          <a href="https://github.com/AbdouMandara" target="_blank" rel="noopener" title="GitHub" class="social-link">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
            </svg>
          </a>
          <a href="https://instagram.com/abdou_mandara" target="_blank" rel="noopener" title="Instagram" class="social-link">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect>
              <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path>
              <circle cx="17.5" cy="6.5" r="1.5"></circle>
            </svg>
          </a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted} from 'vue'
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
const backendStatus = ref('Recherche du backend...')
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

function copyAIResponse() {
  navigator.clipboard.writeText(aiResponse.value)
    .then(() => {
      copiedAIResponse.value = true
      setTimeout(() => {
        copiedAIResponse.value = false
      }, 1500)
    })
    .catch(() => {
      error.value = 'Impossible de copier la réponse de l\'IA pour le moment.'
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
  
  try {
    const response = await fetch(`${apiBase}/generate_prompt`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData),
    })

    if (!response.ok) {
      throw new Error('Erreur lors de la génération du prompt')
    }

    const data = await response.json()
    generatedPrompt.value = data.prompt
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
      headers: { 
        'Content-Type': 'application/json'
      },
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
  width: min(100%, 900px);
  max-width: 100%;
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
}

.result-card-header .small-text {
  margin: 0.25rem 0 0.35rem;
  color: #5a6c7d;
  font-size: 0.9rem;
}
.small-text-error{
  color: #fff;
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
  position: fixed;
  right: 2rem;
  bottom: 2rem;
  width: max-content;
  z-index: 9999;
  padding: 0.5em 0.75em;
  background: #dc2626;
  
}

.error-card h3 {
  color: white;
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
  width: 100%;
  margin: 0;
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

.mobile-hidden {
  display: inline;
}

.mobile-text {
  display: none;
}

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

  .wizard-actions button,
  .actions-right button,
  .result-card-header button {
    width: 100%;
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

  .result-card {
    padding: 0rem;
    display: flex;
    flex-direction: column;
    gap: 0.75em;
  }

  .progress-bar-container {
    padding: 1rem;
  }

  button {
    padding: 0.85rem 1.25rem;
    font-size: 0.9rem;
  }

  .wizard-actions button,
  .actions-right button,
  .result-card-header button,
  .form-add-option button {
    width: 100%;
  }

  .form-add-option {
    gap: 0.65rem;
  }

  .form-add-option input {
    min-width: 0;
    flex: 1 1 100%;
  }

  .action-buttons {
    grid-template-columns: 1fr;
  }

  .error-card {
    position: static;
    width: auto;
    right: auto;
    bottom: auto;
    margin-top: 1rem;
  }

  .mobile-hidden {
    display: none;
  }

  .mobile-text {
    display: inline;
  }
}

.app-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #ffffff;
}

.app-header {
  backdrop-filter: blur(10px);
  border-bottom : 1px solid #d1d5db;
  padding: 1rem;
  /* box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); */
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  justify-content: center;
}

.app-name {
  width : max-content;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  color : #0d7a66;
  padding: 0.5rem 1rem;
  background: #e8f5f1;
  border-radius: 999px;
}

.app-footer {
  border-top: 1px solid #d1d5db;
  color: white;
  padding: 2rem;
  margin-top: auto;
}

.footer-content {
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.footer-content p {
  margin: 0;
  font-size: 0.95rem;
  color: #5a6c7d;
}

.footer-content strong {
  color: #0f8b74;
  font-weight: 600;
}

.social-links {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.social-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(15, 139, 116, 0.1);
  color: #0f8b74;
  transition: all 0.2s ease;
  text-decoration: none;
}

.social-link:hover {
  background: #0f8b74;
  color: white;
}

.social-link svg {
  width: 20px;
  height: 20px;
}

@media (max-width: 640px) {
  .app-header {
    padding: 1rem;
  }

  .app-name {
    font-size: 1rem;
  }

  .app-footer {
    padding: 1.5rem;
  }

  .footer-content {
    flex-direction: column;
    text-align: center;
  }

  .social-links {
    justify-content: center;
    width: 100%;
  }
}
</style>

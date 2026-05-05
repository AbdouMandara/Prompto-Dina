import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCustomOptionsStore = defineStore('customOptions', () => {
  // Charger les données du localStorage ou initialiser vide
  const loadFromStorage = () => {
    try {
      const stored = localStorage.getItem('promptBuilder_customOptions')
      return stored ? JSON.parse(stored) : {}
    } catch (e) {
      console.error('Erreur lors du chargement du localStorage:', e)
      return {}
    }
  }

  const customOptions = ref(loadFromStorage())

  // Sauvegarder dans le localStorage
  const saveToStorage = () => {
    try {
      localStorage.setItem('promptBuilder_customOptions', JSON.stringify(customOptions.value))
    } catch (e) {
      console.error('Erreur lors de la sauvegarde au localStorage:', e)
    }
  }

  // Ajouter une option personnalisée
  const addCustomOption = (stepKey, option) => {
    if (!customOptions.value[stepKey]) {
      customOptions.value[stepKey] = []
    }

    if (!customOptions.value[stepKey].includes(option)) {
      customOptions.value[stepKey].push(option)
      saveToStorage()
    }
  }

  // Obtenir les options personnalisées pour une étape
  const getCustomOptions = (stepKey) => {
    return customOptions.value[stepKey] || []
  }

  // Supprimer une option personnalisée
  const removeCustomOption = (stepKey, option) => {
    if (customOptions.value[stepKey]) {
      customOptions.value[stepKey] = customOptions.value[stepKey].filter(o => o !== option)
      saveToStorage()
    }
  }

  // Réinitialiser toutes les options
  const resetCustomOptions = () => {
    customOptions.value = {}
    localStorage.removeItem('promptBuilder_customOptions')
  }

  return {
    customOptions,
    addCustomOption,
    getCustomOptions,
    removeCustomOption,
    resetCustomOptions,
  }
})

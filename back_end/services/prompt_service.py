from typing import List

from .schemas import PromptRequest


def build_prompt(data: PromptRequest) -> str:
    prompt_lines = [
        f"Rôle : {data.role}.",
        f"Objectif : {data.objective}.",
        f"Niveau de l'utilisateur : {data.level}.",
        f"Format attendu : {data.responseFormat}.",
        f"Ton : {data.tone}.",
        f"Longueur : {data.length}.",
    ]

    if data.constraints.strip():
        prompt_lines.append(f"Contraintes : {data.constraints.strip()}.")

    prompt_lines.extend(
        [
            "A partir de l'idée suivante, génère un prompt optimisé et prêt à l'emploi pour utiliser avec un modèle d'IA.",
            "Le prompt doit être directement utilisable, sans explication préalable.",
            data.idea.strip(),
            "Génère UNIQUEMENT le prompt, sans explication ni préambule.",
        ]
    )

    return "\n".join(prompt_lines)


def suggest_improvements(data: PromptRequest) -> List[str]:
    suggestions = [
        f"Vérifiez que l’objectif '{data.objective}' est bien reflété dans le prompt.",
        "Ajoutez une contrainte de format si nécessaire pour rendre la réponse plus précise.",
        "Utilisez des exemples concrets si vous souhaitez rendre le prompt plus actionnable.",
    ]

    if data.constraints.strip():
        suggestions.append("Confirmez que les contraintes avancées sont correctement intégrées.")

    return suggestions

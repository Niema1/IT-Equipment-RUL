## Description
Ce projet a été réalisé dans le cadre de mon projet de fin d'études à Bank Al-Maghrib.

L'objectif est d'estimer la durée de vie restante (Remaining Useful Life - RUL) des équipements informatiques en analysant leurs performances, leur âge et différents indicateurs de santé afin d'aider à la prise de décision pour le renouvellement du parc informatique.

## Fonctionnalités
- Import des données Excel
- Nettoyage et prétraitement des données
- Calcul des indicateurs de performance
- Classification de l'état des équipements (Bon, Moyen, Mauvais)
- Estimation de la durée de vie restante (RUL)
- Interface utilisateur avec Streamlit
- Export des résultats

## Technologies utilisées
- Python
- Pandas
- NumPy
- Scikit-learn
- Streamlit
- Matplotlib
- Random Forest

##  Structure du projet

```
Estimation-RUL/
│── app.py
│── data/
│── models/
│── utils/
│── requirements.txt
│── README.md
```

##  Méthodologie
Le projet repose sur :
- le prétraitement des données,
- le calcul d'un score de santé des équipements,
- la classification selon leur état,
- l'estimation de la durée de vie restante (RUL).

##  Résultat
Cette application permet d'identifier les équipements nécessitant un remplacement prochain et d'aider à optimiser la gestion du parc informatique.

## Auteur
Niema Berrada
Ingénieure d'État en Génie Informatique – Data Science

## ⚠️ Données
Les jeux de données utilisés durant ce projet ne sont pas inclus dans ce dépôt en raison de leur caractère confidentiel.

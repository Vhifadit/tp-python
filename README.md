# Application de Facturation et Statistiques de Ventes

## Description

Cette application Python en mode console permet de gérer des opérations de facturation, de consultation de données, et de génération de rapports. Elle utilise les bibliothèques Pandas pour la manipulation de fichiers Excel et ReportLab pour la génération de factures en PDF.

## Fonctionnalités

### Menu Principal
1. **Consulter un fichier**
   - Afficher les clients
   - Afficher les produits
   - Afficher les cartes de réduction

2. **Générer une facture**
   - Créer un nouveau client ou sélectionner un client existant
   - Saisir les produits à facturer
   - Application automatique des cartes de réduction
   - Génération de facture en PDF

3. **Ajouter un produit**
   - Ajouter un nouveau produit au catalogue

4. **Statistiques de ventes**
   - Chiffre d'affaires total
   - Moyenne par facture
   - Statistiques par client

5. **Quitter l'application**

## Installation

### Prérequis
- Python 3.7 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner ou télécharger le projet**
   ```bash
   git clone <url-du-repo>
   cd tpp-python
   ```

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancer l'application**
   ```bash
   python main.py
   ```

## Structure des fichiers

```
tpp-python/
├── main.py                 # Application principale
├── data_manager.py         # Gestion des données Excel
├── facture_generator.py    # Génération de factures PDF
├── create_initial_data.py  # Création des données initiales
├── requirements.txt        # Dépendances Python
├── README.md              # Documentation
├── data/                  # Dossier des fichiers Excel
│   ├── Clients.xlsx
│   ├── Produits.xlsx
│   ├── CartesReduction.xlsx
│   └── Factures.xlsx
└── factures/              # Dossier des factures PDF générées
```

## Fichiers de données

### Clients.xlsx
- `code_client` : Identifiant unique du client
- `nom` : Nom de l'entreprise/client
- `contact` : Email ou téléphone
- `IFU` : Identifiant Fiscal Unique (13 caractères)

### Produits.xlsx
- `code_produit` : Code produit (6 caractères)
- `libelle` : Description du produit
- `prix_unitaire` : Prix unitaire en FCFA

### CartesReduction.xlsx
- `numero_carte` : Numéro unique de la carte
- `code_client` : Référence au client
- `taux_reduction` : Pourcentage de réduction

## Système de cartes de réduction

Les cartes de réduction sont créées automatiquement selon les montants des factures :

- **≥ 10 000 FCFA** : 15% de réduction
- **≥ 5 000 FCFA** : 10% de réduction  
- **≥ 2 000 FCFA** : 5% de réduction
- **< 2 000 FCFA** : Aucune carte

**Note importante** : Aucune remise n'est appliquée sur la première facture d'un client, même si elle entraîne la création d'une carte.

## Utilisation

### Première utilisation
Lors du premier lancement, l'application crée automatiquement :
- Le dossier `data/` avec les fichiers Excel initiaux
- 2 clients de démonstration
- 10 produits de démonstration

### Génération d'une facture
1. Choisir "Générer une facture" dans le menu principal
2. Sélectionner un client existant ou créer un nouveau client
3. Saisir les produits à facturer (code + quantité)
4. Vérifier le récapitulatif
5. Confirmer la génération

La facture PDF sera créée dans le dossier `factures/` avec le format :
- En-tête avec nom du groupe et date
- Informations du client
- Tableau des produits avec totaux
- Calculs automatiques (TVA 18%, remises)
- Total en lettres

### Ajout de produits
- Code produit : exactement 6 caractères
- Libellé : description du produit
- Prix unitaire : nombre positif

## Dépendances

- **pandas** : Manipulation des données Excel
- **openpyxl** : Lecture/écriture de fichiers Excel
- **reportlab** : Génération de PDF
- **xlsxwriter** : Écriture avancée d'Excel

## Extensions possibles

1. **Statistiques avancées** : Produit le plus vendu, tendances
2. **Historique des factures** : Consultation des factures passées
3. **Interface graphique** : Version avec Tkinter
4. **Export de données** : CSV, JSON, etc.
5. **Gestion des stocks** : Suivi des quantités disponibles

## Support

Pour toute question ou problème, consultez la documentation ou contactez l'équipe de développement.

## Licence

Ce projet est développé dans le cadre d'un travail pédagogique. 
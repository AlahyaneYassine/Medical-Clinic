# Medical Clinic

> Plateforme de gestion de cabinet médical

Application web Django de prise de rendez-vous et de gestion de cabinet médical, avec trois espaces distincts : patient, médecin et réceptionniste.

## Fonctionnalités

**Patient**
- Inscription, connexion et changement de mot de passe
- Recherche de médecins par spécialité et par ville
- Réservation de rendez-vous sur des créneaux de 30 minutes, dans les horaires du médecin
- Historique des rendez-vous (à venir, passés, annulés)
- Avis et note sur un médecin, possibles uniquement après un rendez-vous confirmé passé (la note moyenne du médecin est recalculée)

**Médecin**
- Inscription avec validation manuelle par un administrateur (compte inactif tant qu'il n'est pas activé)
- Tableau de bord : rendez-vous du jour, à venir, en attente, annulés
- Confirmation et annulation des rendez-vous
- Liste de ses patients, notes libres et dossier médical (antécédents, traitements, allergies)
- Création de comptes réceptionniste

**Réceptionniste**
- Tableau de bord des rendez-vous du médecin auquel il est rattaché
- Confirmation / annulation de rendez-vous
- Création de comptes patient

**Administration** : interface d'administration Django (médecins, patients, réceptionnistes, rendez-vous).

## Stack technique

- Python 3, Django 5.1
- SQLite (base locale)
- Templates Django (HTML/CSS/JavaScript), Font Awesome et Google Fonts via CDN
- `python-dotenv` pour la configuration par variables d'environnement

## Architecture

```
├── manage.py
├── monCabinet_medical/      # Configuration du projet (settings, urls, wsgi/asgi)
├── gestion/                 # Application principale
│   ├── models.py            # Patient, Medecin, Rendezvous, Receptionniste, Avis, NoteMedicale, DossierMedical
│   ├── views.py             # Vues (inscription, connexions, dashboards, rendez-vous, dossiers, avis)
│   ├── forms.py             # Formulaires (disponibilités, réceptionniste, rendez-vous)
│   ├── admin.py             # Configuration de l'admin Django
│   └── migrations/
├── templates/               # Pages HTML (accueil, login, dashboards, réservation, dossier médical...)
├── requirements.txt
└── .env.example             # Modèle de configuration
```

## Prérequis

- Python 3.10 ou supérieur
- pip

## Installation et lancement

```bash
git clone https://github.com/AlahyaneYassine/Medical-Clinic.git
cd Medical-Clinic

python -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env            # puis renseigner DJANGO_SECRET_KEY

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

L'application est accessible sur http://127.0.0.1:8000/. Une clé secrète peut être générée avec :

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Utilisation

- Patients : `/inscription/` puis `/login/`
- Médecins et réceptionnistes : `/staff_login/` (un médecin s'inscrit via `/register_medecin/`, puis un administrateur active son compte dans `/admin/`)
- Administration : `/admin/`

## Limitations connues et pistes d'amélioration

- Les comptes médecin et réceptionniste utilisent des sessions personnalisées ; migrer vers le système d'authentification Django avec des groupes/permissions permettrait des contrôles d'accès homogènes.
- Les contrôles d'accès de certaines vues et les opérations qui modifient des données via des requêtes GET (confirmation, annulation) sont à durcir (méthode POST, protection CSRF, vérification de propriété).
- La couverture de tests est à construire (`gestion/tests.py` est vide).
- Le projet est configuré pour le développement (SQLite, `DEBUG` activé par défaut) ; un déploiement demanderait PostgreSQL, un serveur WSGI et `DEBUG=False`.
- Les données médicales ne sont pas chiffrées au repos.
- Projet pédagogique : ne pas l'utiliser avec de vraies données de patients en l'état.

## Auteur

Yassine Alahyane
Cybersecurity Engineering Student

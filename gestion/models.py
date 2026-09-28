from django.db import models
from django.contrib.auth.models import User


# -------------------
# Patient
# -------------------
class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    date_naissance = models.DateField()
    adresse = models.CharField(max_length=255)
    telephone = models.CharField(max_length=20)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.prenom} {self.nom}"


# -------------------
# Médecin
# -------------------
SPECIALITE_CHOICES = [
    ('cardiologie', 'Cardiologie'),
    ('dermatologie', 'Dermatologie'),
    ('généraliste', 'Généraliste'),
    ('pédiatre', 'Pédiatre'),
    ('chirurgie', 'Chirurgie'),
]

class Medecin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="medecin_profile")
    telephone = models.CharField(max_length=15)
    specialite = models.CharField(max_length=50, choices=SPECIALITE_CHOICES)
    ville = models.CharField(max_length=100)
    adresse = models.CharField(max_length=255)
    heure_debut = models.TimeField(default='08:00')
    heure_fin = models.TimeField(default='18:00')
    date_creation = models.DateTimeField(auto_now_add=True)
    note = models.FloatField(default=4.7)
    actif = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.specialite})"


# -------------------
# Rendez-vous
# -------------------
STATUS_CHOICES = [
    ('Confirmé', 'Confirmé'),
    ('En attente', 'En attente'),
    ('Annulé', 'Annulé'),
]

class Rendezvous(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='rendezvous_patient')
    medecin = models.ForeignKey(Medecin, on_delete=models.CASCADE, related_name='rendezvous_medecin')
    date_heure = models.DateTimeField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='En attente')

    def __str__(self):
        return f"RDV de {self.patient} avec Dr. {self.medecin.user.first_name} le {self.date_heure.strftime('%Y-%m-%d %H:%M')}"

    @staticmethod
    def is_available(medecin, date_heure):
        return not Rendezvous.objects.filter(medecin=medecin, date_heure=date_heure).exists()


# -------------------
# Réceptionniste
# -------------------
class Receptionniste(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    medecin = models.ForeignKey(Medecin, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.prenom} {self.nom}"


# -------------------
# Avis
# -------------------
class Avis(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    medecin = models.ForeignKey(Medecin, on_delete=models.CASCADE)
    note = models.IntegerField()
    commentaire = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} - {self.medecin} : {self.note}"


# -------------------
# Notes médicales (libres)
# -------------------
class NoteMedicale(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    medecin = models.ForeignKey(Medecin, on_delete=models.CASCADE)
    texte = models.TextField()
    date = models.DateTimeField(auto_now_add=True)


# -------------------
# Dossier médical complet
# -------------------
class DossierMedical(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE)
    antecedents = models.TextField(blank=True)
    traitements = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    autres_notes = models.TextField(blank=True)

    def __str__(self):
        return f"Dossier médical de {self.patient}"

from django.contrib import admin
from .models import Medecin, Rendezvous, Patient, Receptionniste

@admin.register(Medecin)
class MedecinAdmin(admin.ModelAdmin):
    list_display = ('nom_complet', 'email', 'specialite', 'ville', 'actif', 'date_creation')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'specialite')
    list_filter = ('actif', 'specialite', 'ville')
    list_editable = ('actif',)

    fields = (
        'user',             # Utilisateur associé
        'telephone',
        'specialite',
        'ville',
        'adresse',
        'heure_debut',
        'heure_fin',
        'actif',            # ✅ pour pouvoir le modifier depuis l'admin
    )

    def nom_complet(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    nom_complet.short_description = "Nom"

    def email(self, obj):
        return obj.user.email

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email', 'telephone')

@admin.register(Receptionniste)
class ReceptionnisteAdmin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'medecin')
    list_filter = ('medecin',)
    search_fields = ('nom', 'email')

@admin.register(Rendezvous)
class RendezvousAdmin(admin.ModelAdmin):
    list_display = ('medecin', 'patient', 'date_heure', 'status')
    list_filter = ('status', 'date_heure', 'medecin')

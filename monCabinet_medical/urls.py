from django.contrib import admin
from django.urls import path
from gestion import views




urlpatterns = [
    
    path('', views.index, name='index'),  # page d'accueil
    path('admin/', admin.site.urls),

    # Inscriptions
    path('inscription/', views.inscription, name='inscription'),
    path('register_medecin/', views.register_medecin, name='register_medecin'),

    # Connexions
    path('login/', views.patient_login, name='login'),  # login patient
    path('staff_login/', views.staff_login, name='staff_login'),  # login staff (médecin / réceptionniste)

    # Dashboards
    path('main/', views.main_page, name='main'),  # dashboard patient
    path('page_medecin/', views.medecin_dashboard, name='page_medecin'),  # dashboard médecin
    path('receptionniste_dashboard/', views.receptionniste_dashboard, name='receptionniste_dashboard'),  # dashboard réceptionniste

    # Déconnexion
    path('logout/', views.logout_view, name='logout'),

    ##anuuker
    path('annuler_rdv/<int:rdv_id>/', views.annuler_rdv, name='annuler_rdv'),



    ##prendreRDV
    path('medecin/<int:medecin_id>/reserver/', views.reserver_rdv, name='reserver_rdv'),


    ##api
    path('api/heures-disponibles/', views.get_heures_disponibles, name='get_heures_disponibles'),


    path('confirmer_rdv/<int:rdv_id>/', views.confirmer_rdv, name='confirmer_rdv'),
    #cration de compte patient par le staff
    path('ajouter_patient/', views.ajouter_patient, name='ajouter_patient'),

    #voir les rendez-vous clinet
    path('patient/historique/', views.historique_rdv, name='historique_rdv'),

##mon compte
    path('mon-compte/', views.mon_compte, name='mon_compte'),
##ajouter rece
    path('medecin/ajouter-receptionniste/', views.ajouter_receptionniste, name='ajouter_receptionniste'),

    # Gestion des rendez-vous
    path("patients/", views.mes_patients, name="mes_patients"),
    path("patient/<int:patient_id>/notes/", views.editer_notes_patient, name="editer_notes_patient"),
    #avis
    path('medecin/<int:medecin_id>/profil/', views.laisser_avis, name='laisser_avis'),
##dossier
    path('medecin/patient/<int:patient_id>/dossier/', views.voir_dossier_patient, name='voir_dossier_patient'),

    

    






]
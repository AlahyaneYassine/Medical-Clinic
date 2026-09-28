import secrets
from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password, check_password
from .models import Medecin, Receptionniste
from .forms import RendezvousForm
from django.contrib.auth.decorators import login_required
from .models import Patient


# ---------------------- INSCRIPTION PATIENT ----------------------



def inscription(request):
    if request.method == "POST":
        nom = request.POST['nom']
        prenom = request.POST['prenom']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        date_naissance = request.POST['date_naissance']
        adresse = request.POST['adresse']
        telephone = request.POST['telephone']

        if password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('inscription')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return redirect('inscription')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=prenom,
            last_name=nom
        )

        Patient.objects.create(
            user=user,
            nom=nom,
            prenom=prenom,
            email=email,
            date_naissance=date_naissance,
            adresse=adresse,
            telephone=telephone
        )

        messages.success(request, "Compte patient créé avec succès. Connectez-vous maintenant.")
        return redirect('login')

    return render(request, 'inscription.html')


# ---------------------- CONNEXION PATIENT ----------------------

def patient_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('main')
        else:
            messages.error(request, 'Email ou mot de passe incorrect.')

    return render(request, 'login.html')


# ---------------------- CONNEXION STAFF (MEDECIN / RECEPTIONNISTE) ----------------------
from django.contrib.auth import authenticate

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

def staff_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if role == 'medecin':
            try:
                medecin = Medecin.objects.get(user__email=email)
                if medecin.user.check_password(password):
                    if medecin.user.is_active:
                        request.session['medecin_id'] = medecin.id
                        return redirect('page_medecin')
                    else:
                        messages.error(request, "Votre compte n'a pas encore été activé.")
                else:
                    messages.error(request, "Mot de passe incorrect.")
            except Medecin.DoesNotExist:
                messages.error(request, "Médecin non trouvé.")

        elif role == 'receptionniste':
            try:
                receptionniste = Receptionniste.objects.get(email=email)
                if check_password(password, receptionniste.password):
                    request.session['receptionniste_id'] = receptionniste.id
                    return redirect('receptionniste_dashboard')
                else:
                    messages.error(request, "Mot de passe incorrect.")
            except Receptionniste.DoesNotExist:
                messages.error(request, "Réceptionniste non trouvé.")

        else:
            messages.error(request, "Rôle invalide.")

    return render(request, 'medecinLogin.html')

# ---------------------- INSCRIPTION MEDECIN ----------------------

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Medecin

from .models import Medecin, SPECIALITE_CHOICES

def register_medecin(request):
    if request.method == 'POST':
        prenom = request.POST.get('prenom')
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        password = request.POST.get('password')
        telephone = request.POST.get('telephone')
        specialite = request.POST.get('specialite')
        ville = request.POST.get('ville')
        adresse = request.POST.get('adresse')
        heure_debut = request.POST.get('heure_debut')
        heure_fin = request.POST.get('heure_fin')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Un compte avec cet email existe déjà.")
            return redirect('register_medecin')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=prenom,
            last_name=nom
        )
        user.is_active = False  # 🛑 En attente d'activation manuelle par un admin
        user.save()

        Medecin.objects.create(
            user=user,
            telephone=telephone,
            specialite=specialite,
            ville=ville,
            adresse=adresse,
            heure_debut=heure_debut,
            heure_fin=heure_fin
        )

        messages.success(request, "Compte médecin créé ! En attente de validation par un administrateur.")
        return redirect('staff_login')

    # 🧠 Convertir la liste en dictionnaire pour affichage dans le template
    specialites = dict(SPECIALITE_CHOICES)
    return render(request, 'register_medecin.html', {
        'specialites': specialites
    })
# ---------------------- DASHBOARDS ----------------------



def main_page(request):
    specialite = request.GET.get('specialite')
    ville = request.GET.get('ville')

    medecins = Medecin.objects.all()
    if specialite:
        medecins = medecins.filter(specialite=specialite)
    if ville:
        medecins = medecins.filter(ville=ville)

    # liste unique pour les filtres
    specialites = Medecin.objects.values_list('specialite', flat=True).distinct()
    villes = Medecin.objects.values_list('ville', flat=True).distinct()

    return render(request, 'main.html', {
        'medecins': medecins,
        'specialites': specialites,
        'villes': villes,
        'selected_specialite': specialite,
        'selected_ville': ville,
    })

from .models import Rendezvous, Medecin
from django.utils.timezone import now
from django.db.models import Q
from datetime import timedelta

from django.utils.timezone import now, timedelta

def medecin_dashboard(request):
    medecin_id = request.session.get('medecin_id')
    if not medecin_id:
        return redirect('staff_login')

    medecin = Medecin.objects.get(id=medecin_id)
    today = now().date()

    Rendezvous.objects.filter(status='Annulé', date_heure__lt=now() - timedelta(days=7)).delete()

    # Tous les RDV du médecin
    rendezvous_all = Rendezvous.objects.filter(medecin=medecin).order_by('date_heure')

    # Statistiques
    rdv_aujourdhui_qs = rendezvous_all.filter(date_heure__date=today).exclude(status='Annulé')
    en_attente = rendezvous_all.filter(status='En attente').count()
    annules = rendezvous_all.filter(status='Annulé').count()
    satisfaction = medecin.note  # ou moyenne basée sur avis

    # Prochains RDV = dans le futur, hors aujourd’hui
    prochains_rdv = rendezvous_all.filter(date_heure__date__gt=today).exclude(status='Annulé')

    return render(request, 'page_medecin.html', {
        'medecin': medecin,
        'rdv_aujourdhui_list': rdv_aujourdhui_qs,
        'rdv_futurs': prochains_rdv,
        'rdv_aujourdhui': rdv_aujourdhui_qs.count(),
        'en_attente': en_attente,
        'annules': annules,
        'satisfaction': satisfaction,
    })


# ---------------------- DECONNEXION ----------------------
def logout_view(request):
    is_medecin = request.session.get('medecin_id')
    is_receptionniste = request.session.get('receptionniste_id')

    # Supprimer les sessions personnalisées
    request.session.pop('medecin_id', None)
    request.session.pop('receptionniste_id', None)

    list(messages.get_messages(request))

    # Déconnexion pour le patient (login via auth)
    logout(request)

    # Rediriger correctement
    if is_medecin or is_receptionniste:
        return redirect('staff_login')
    return redirect('login')


# ---------------------- ANNULER UN RENDEZ-VOUS ----------------------
def annuler_rdv(request, rdv_id):
    medecin_id = request.session.get('medecin_id')
    receptionniste_id = request.session.get('receptionniste_id')

    if not medecin_id and not receptionniste_id:
        return redirect('staff_login')

    try:
        if medecin_id:
            rdv = Rendezvous.objects.get(id=rdv_id, medecin_id=medecin_id)
        else:
            receptionniste = Receptionniste.objects.get(id=receptionniste_id)
            rdv = Rendezvous.objects.get(id=rdv_id, medecin=receptionniste.medecin)

        rdv.status = 'Annulé'
        rdv.save()
        messages.success(request, "Rendez-vous annulé.")
    except Rendezvous.DoesNotExist:
        messages.error(request, "Rendez-vous introuvable.")

    return redirect('receptionniste_dashboard' if receptionniste_id else 'page_medecin')



from .forms import DisponibiliteForm
from django.utils import timezone

@login_required
def reserver_rdv(request, medecin_id):
    print(">>> Appel réussi à reserver_rdv")

    print(">>> Entrée dans reserver_rdv")

    medecin = get_object_or_404(Medecin, id=medecin_id)

    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, "Profil patient introuvable.")
        return redirect('main')

    print(">>> Patient trouvé :", patient)

    if request.method == 'POST':
        print(">>> Formulaire POST reçu")
        form = DisponibiliteForm(request.POST, medecin=medecin)
        if form.is_valid():
            print(">>> Formulaire valide")
            date = form.cleaned_data['date']
            heure_str = form.cleaned_data['heure']
            date_heure = timezone.datetime.combine(date, timezone.datetime.strptime(heure_str, '%H:%M').time())

            if Rendezvous.is_available(medecin, date_heure):
                Rendezvous.objects.create(
                    medecin=medecin,
                    patient=patient,
                    date_heure=date_heure,
                    status='En attente'
                )
                messages.success(request, "Votre rendez-vous a été enregistré.")
                return redirect('reserver_rdv', medecin_id=medecin.id)
            else:
                messages.error(request, "Ce créneau est déjà pris.")
        else:
            print(">>> Formulaire invalide :", form.errors)
    else:
        form = DisponibiliteForm(medecin=medecin)

    return render(request, 'reserver_rdv.html', {'form': form, 'medecin': medecin})


from django.http import JsonResponse
from .models import Rendezvous
import datetime

def get_heures_disponibles(request):
    medecin_id = request.GET.get('medecin')
    date_str = request.GET.get('date')

    try:
        medecin = Medecin.objects.get(id=medecin_id)
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        heures = []

        start = datetime.datetime.combine(date, medecin.heure_debut)
        end = datetime.datetime.combine(date, medecin.heure_fin)

        while start < end:
            if Rendezvous.is_available(medecin, start):
                heures.append(start.strftime('%H:%M'))
            start += datetime.timedelta(minutes=30)

        return JsonResponse({'heures': heures})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)




##patient
def index(request):
    return render(request, 'index.html')

from .models import Receptionniste

def receptionniste_dashboard(request):
    receptionniste_id = request.session.get('receptionniste_id')
    if not receptionniste_id:
        return redirect('staff_login')

    receptionniste = Receptionniste.objects.get(id=receptionniste_id)
    
    return render(request, 'receptionniste_dashboard.html', {
        'receptionniste': receptionniste
    })
def confirmer_rdv(request, rdv_id):
    medecin_id = request.session.get('medecin_id')
    receptionniste_id = request.session.get('receptionniste_id')

    if not medecin_id and not receptionniste_id:
        return redirect('staff_login')

    try:
        if medecin_id:
            rdv = Rendezvous.objects.get(id=rdv_id, medecin_id=medecin_id)
        else:
            receptionniste = Receptionniste.objects.get(id=receptionniste_id)
            rdv = Rendezvous.objects.get(id=rdv_id, medecin=receptionniste.medecin)

        rdv.status = 'Confirmé'
        rdv.save()
        messages.success(request, "Rendez-vous confirmé.")
    except Rendezvous.DoesNotExist:
        messages.error(request, "Rendez-vous introuvable.")

    return redirect('receptionniste_dashboard' if receptionniste_id else 'page_medecin')



#creation client par staff
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

def ajouter_patient(request):
    # Réservé aux réceptionnistes connectés
    receptionniste_id = request.session.get('receptionniste_id')
    if not receptionniste_id:
        return redirect('staff_login')

    receptionniste = Receptionniste.objects.filter(id=receptionniste_id).first()
    if receptionniste is None:
        return redirect('staff_login')

    if request.method == 'POST':
        nom = request.POST.get('nom', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        email = request.POST.get('email', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        adresse = request.POST.get('adresse', '').strip()
        date_naissance = request.POST.get('date_naissance', '').strip()

        if not (nom and prenom and email and date_naissance):
            messages.error(request, "Nom, prénom, email et date de naissance sont obligatoires.")
            return redirect('ajouter_patient')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            return redirect('ajouter_patient')

        # Mot de passe temporaire aléatoire, différent pour chaque patient
        mot_de_passe_temp = secrets.token_urlsafe(9)

        user = User.objects.create_user(
            username=email,
            email=email,
            password=mot_de_passe_temp,
            first_name=prenom,
            last_name=nom,
        )

        Patient.objects.create(
            user=user,
            nom=nom,
            prenom=prenom,
            email=email,
            telephone=telephone,
            adresse=adresse,
            date_naissance=date_naissance,
        )

        messages.success(
            request,
            f"Patient ajouté. Mot de passe temporaire : {mot_de_passe_temp} "
            "(à communiquer au patient, qui pourra le changer dans « Mon compte »)."
        )
        return redirect('ajouter_patient')

    return render(request, 'ajouter_patient.html', {'receptionniste': receptionniste})

from django.utils.timezone import now

def receptionniste_dashboard(request):
    receptionniste_id = request.session.get('receptionniste_id')
    if not receptionniste_id:
        return redirect('staff_login')

    try:
        receptionniste = Receptionniste.objects.get(id=receptionniste_id)
    except Receptionniste.DoesNotExist:
        messages.error(request, "Réceptionniste introuvable.")
        return redirect('staff_login')

    medecin = receptionniste.medecin
    today = now().date()

    rdv_aujourdhui = Rendezvous.objects.filter(
        medecin=medecin, date_heure__date=today
    ).exclude(status='Annulé')

    rdv_futurs = Rendezvous.objects.filter(
        medecin=medecin, date_heure__date__gt=today
    ).exclude(status='Annulé')

    rdv_annules = Rendezvous.objects.filter(
        medecin=medecin, status='Annulé'
    ).order_by('-date_heure')

    return render(request, 'receptionniste_dashboard.html', {
        'receptionniste': receptionniste,
        'rdv_aujourdhui': rdv_aujourdhui,
        'rdv_futurs': rdv_futurs,
        'rdv_annules': rdv_annules,
    })



from django.contrib.auth.decorators import login_required
from .models import Rendezvous, Patient

@login_required
def historique_rdv(request):
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, "Patient introuvable.")
        return redirect('main')

    # Tous les rendez-vous du patient (triés par date décroissante)
    rendezvous = Rendezvous.objects.filter(patient=patient).order_by('-date_heure')

    return render(request, 'historique_rdv.html', {'rendezvous': rendezvous})



from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


@login_required
def mon_compte(request):
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, "Profil patient introuvable.")
        return redirect('main')

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Pour éviter la déconnexion
            messages.success(request, 'Mot de passe modifié avec succès.')
            return redirect('mon_compte')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'mon_compte.html', {
        'patient': patient,
        'form': form,
    })



##ajouter receptioniste a partir du medcin
from .forms import ReceptionnisteForm
from django.contrib import messages
from .models import Medecin, Receptionniste

def ajouter_receptionniste(request):
    medecin_id = request.session.get('medecin_id')
    if not medecin_id:
        return redirect('staff_login')

    medecin = Medecin.objects.get(id=medecin_id)

    if request.method == 'POST':
        form = ReceptionnisteForm(request.POST)
        if form.is_valid():
            receptionniste = form.save(commit=False)
            receptionniste.medecin = medecin
            receptionniste.password = make_password(form.cleaned_data['password'])
            receptionniste.save()
            messages.success(request, "Réceptionniste ajouté avec succès.")
            return redirect('page_medecin')
    else:
        form = ReceptionnisteForm()

    return render(request, 'ajouter_receptionniste.html', {'form': form})


##annulerhrdv
from .models import Rendezvous, Patient
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now

@login_required
def historique_rdv(request):
    patient = Patient.objects.get(user=request.user)

    aujourd_hui = now()

    # RDV à venir (date future et statut pas annulé)
    rdv_futurs = Rendezvous.objects.filter(
        patient=patient,
        date_heure__gte=aujourd_hui,
    ).exclude(status='Annulé').order_by('date_heure')

    # Historique = tous les anciens rendez-vous ou annulés
    rdv_historiques = Rendezvous.objects.filter(
        patient=patient,
        date_heure__lt=aujourd_hui
    ) | Rendezvous.objects.filter(patient=patient, status='Annulé')

    rdv_historiques = rdv_historiques.order_by('-date_heure')

    return render(request, 'historique_rdv.html', {
        'rdv_futurs': rdv_futurs,
        'rdv_historiques': rdv_historiques,
    })

from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Rendezvous, Patient

@login_required
def annuler_rdv_patient(request, rdv_id):
    patient = get_object_or_404(Patient, user=request.user)
    try:
        rdv = Rendezvous.objects.get(id=rdv_id, patient=patient)
        rdv.status = 'Annulé'
        rdv.save()
        messages.success(request, "Votre rendez-vous a été annulé.")
    except Rendezvous.DoesNotExist:
        messages.error(request, "Rendez-vous introuvable.")
    return redirect('historique_rdv')


##notePatientfrom django.shortcuts import render, get_object_or_404, redirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Patient, Medecin

from django.db.models import Q
from django.shortcuts import render
from .models import Patient, Rendezvous, Medecin

def mes_patients(request):
    medecin_id = request.session.get('medecin_id')
    if not medecin_id:
        return redirect('staff_login')  # Ou une autre redirection

    # Trouver tous les patients qui ont pris un rendez-vous avec ce médecin
    patients = Patient.objects.filter(
        rendezvous_patient__medecin_id=medecin_id
    ).distinct()

    context = {
        'patients': patients
    }
    return render(request, 'mes_patients.html', context)


def editer_notes_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == "POST":
        notes = request.POST.get("notes")
        patient.notes = notes
        patient.save()
        return redirect("mes_patients")
    return render(request, "editer_notes.html", {"patient": patient})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now
from .models import Medecin, Patient, Rendezvous, Avis

from django.db.models import Avg  # à ajouter en haut si pas déjà

@login_required
def laisser_avis(request, medecin_id):
    medecin = get_object_or_404(Medecin, id=medecin_id)
    avis = Avis.objects.filter(medecin=medecin).order_by('-date')

    # Vérifier que c'est bien un patient
    if not hasattr(request.user, 'patient'):
        messages.error(request, "Seuls les patients peuvent laisser un avis.")
        return redirect('main')

    patient = request.user.patient

    # Le patient peut-il noter ?
    peut_noter = Rendezvous.objects.filter(
        patient=patient,
        medecin=medecin,
        status='Confirmé',
        date_heure__lt=now()
    ).exists()

    if request.method == 'POST':
        if not peut_noter:
            messages.error(request, "Vous ne pouvez noter ce médecin que si vous avez eu un rendez-vous confirmé dans le passé.")
            return redirect('laisser_avis', medecin_id=medecin.id)

        note = int(request.POST.get('note'))
        commentaire = request.POST.get('commentaire', '')

        if not Avis.objects.filter(patient=patient, medecin=medecin).exists():
            Avis.objects.create(patient=patient, medecin=medecin, note=note, commentaire=commentaire)

            # 🔄 Mise à jour de la moyenne
            moyenne = Avis.objects.filter(medecin=medecin).aggregate(Avg('note'))['note__avg']
            medecin.note = moyenne
            medecin.save()

            messages.success(request, "Merci pour votre avis.")
        else:
            messages.info(request, "Vous avez déjà laissé un avis pour ce médecin.")
        return redirect('laisser_avis', medecin_id=medecin.id)

    return render(request, 'laisser_avis.html', {
        'medecin': medecin,
        'avis': avis,
        'peut_noter': peut_noter
    })

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Patient, DossierMedical

from django.utils.timezone import now
from .models import Rendezvous


def voir_dossier_patient(request, patient_id):
    if not request.session.get('medecin_id'):
        return redirect('staff_login')
    patient = get_object_or_404(Patient, id=patient_id)
    dossier, _ = DossierMedical.objects.get_or_create(patient=patient)

    # 🧮 Nombre de visites confirmées dans le passé
    nombre_visites = Rendezvous.objects.filter(
        patient=patient,
        status='Confirmé',
        date_heure__lt=now()
    ).count()

    if request.method == 'POST':
        dossier.antecedents = request.POST.get('antecedents', '')
        dossier.traitements = request.POST.get('traitements', '')
        dossier.allergies = request.POST.get('allergies', '')
        dossier.autres_notes = request.POST.get('autres_notes', '')
        dossier.save()
        messages.success(request, "Dossier médical mis à jour.")
        return redirect('voir_dossier_patient', patient_id=patient.id)

    return render(request, 'dossier_medical.html', {
        'patient': patient,
        'dossier': dossier,
        'nombre_visites': nombre_visites  # 👈 on envoie la variable au template
    })

from django import forms
from .models import Rendezvous
from django.utils import timezone

class PatientRegistrationForm(forms.Form):
    lastname = forms.CharField(max_length=100, label='Nom')
    firstname = forms.CharField(max_length=100, label='Prénom')
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Mot de passe')
    birthdate = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label='Date de naissance')
    address = forms.CharField(max_length=255, label='Adresse')
    phone = forms.CharField(max_length=20, label='Téléphone')




class RendezvousForm(forms.ModelForm):
    class Meta:
        model = Rendezvous
        fields = ['date_heure']
        widgets = {
            'date_heure': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_heure'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['date_heure'].required = True

    def clean_date_heure(self):
        date_heure = self.cleaned_data['date_heure']
        if date_heure < timezone.now():
            raise forms.ValidationError("La date et l'heure doivent être dans le futur.")
        return date_heure


from django import forms
from django.utils import timezone
from .models import Rendezvous

class DisponibiliteForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Date"
    )
    heure = forms.ChoiceField(
        choices=[],
        label="Heure disponible"
    )

    def __init__(self, *args, **kwargs):
        medecin = kwargs.pop('medecin')
        super().__init__(*args, **kwargs)

        now = timezone.now()
        today = now.date()
        heure_choices = []

        if 'date' in self.data:
            try:
                selected_date = timezone.datetime.strptime(self.data['date'], '%Y-%m-%d').date()
                if selected_date >= today:
                    start = medecin.heure_debut
                    end = medecin.heure_fin

                    # construire des créneaux de 30 min
                    heure = timezone.datetime.combine(selected_date, start)
                    fin = timezone.datetime.combine(selected_date, end)

                    while heure < fin:
                        h_str = heure.strftime('%H:%M')
                        # on pourrait filtrer ici les créneaux déjà pris (voir étape suivante)
                        heure_choices.append((h_str, h_str))
                        heure += timezone.timedelta(minutes=30)

            except ValueError:
                pass

        self.fields['heure'].choices = heure_choices


from django import forms
from .models import Receptionniste

class ReceptionnisteForm(forms.ModelForm):
    class Meta:
        model = Receptionniste
        fields = ['prenom', 'nom', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(attrs={'placeholder': 'Mot de passe'}),
        }

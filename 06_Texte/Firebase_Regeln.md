# Firebase-Regeln (Silescrow ID – gilt für alle Silescrow-Spiele)

Projekt: **silescrow-cup** · Firestore Database → Reiter „Regeln“ → alles ersetzen → „Veröffentlichen“.
Veröffentlicht am 26.11.2026. Neue Spiele brauchen **keine** neuen Regeln: jedes Spiel nutzt automatisch `spiele/<spiel>/…` (Earth Empire: `spiele/earth-empire/…`).

Admin werden: In der Konsole unter Firestore die Sammlung `admins` öffnen und ein Dokument mit deiner UID als Namen anlegen (Inhalt egal).

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    function an() { return request.auth != null; }
    function konto() { return an() && request.auth.token.firebase.sign_in_provider == 'password'; }
    function admin() { return an() && exists(/databases/$(database)/documents/admins/$(request.auth.uid)); }
    function ich(uid) { return an() && request.auth.uid == uid; }
    function gesperrt() { return an() && exists(/databases/$(database)/documents/sperren/$(request.auth.uid)); }

    // ===== GEMEINSAM FÜR ALLE SPIELE =====
    match /namen/{name} {
      allow read: if true;
      allow create: if konto() && request.resource.data.uid == request.auth.uid;
      allow update, delete: if (konto() && resource.data.uid == request.auth.uid) || admin();
    }
    match /spieler/{uid} { allow read, write: if ich(uid) || admin(); }
    match /liste/{uid} { allow read, write: if ich(uid) || admin(); }
    match /praesenz/{uid} { allow read: if konto(); allow write: if ich(uid); }
    match /freunde/{uid}/liste/{fid} { allow read: if ich(uid); allow write: if ich(uid) || ich(fid); }
    match /anfragen/{ziel}/von/{von} {
      allow read: if ich(ziel) || ich(von);
      allow create, update: if konto() && ich(von);
      allow delete: if ich(ziel) || ich(von);
    }
    match /einladungen/{ziel}/von/{von} {
      allow read: if ich(ziel) || ich(von);
      allow create, update: if konto() && ich(von);
      allow delete: if ich(ziel) || ich(von);
    }
    match /raeume/{uid} { allow read: if konto(); allow write: if konto() && ich(uid); }
    match /geschenke/{uid}/liste/{id} { allow read, delete: if ich(uid) || admin(); allow create, update: if admin(); }
    match /codes/{code} { allow read: if konto(); allow update: if konto() || admin(); allow create, delete: if admin(); }
    match /admins/{uid} { allow read: if ich(uid); allow write: if false; }
    match /sperren/{uid} { allow read: if ich(uid) || admin(); allow write: if admin(); }
    match /support/{uid} { allow read, write: if ich(uid) || admin(); }
    match /support/{uid}/nachrichten/{id} { allow read, write: if ich(uid) || admin(); }

    // ===== JEDES WEITERE SPIEL (Earth Empire, Siles Island, ...) =====
    match /spiele/{spiel}/news/{id} { allow read: if true; allow write: if admin(); }
    match /spiele/{spiel}/spieler/{uid} { allow read: if ich(uid) || admin(); allow write: if (ich(uid) && !gesperrt()) || admin(); }
    match /spiele/{spiel}/liste/{uid} { allow read, write: if ich(uid) || admin(); }
    match /spiele/{spiel}/raeume/{uid} { allow read: if konto(); allow write: if (konto() && ich(uid) && !gesperrt()) || admin(); }
    match /spiele/{spiel}/geschenke/{uid}/liste/{id} { allow read, delete: if ich(uid) || admin(); allow create, update: if admin(); }
    match /spiele/{spiel}/befehle/{uid}/liste/{id} { allow read, delete: if ich(uid) || admin(); allow create, update: if admin(); }
    match /spiele/{spiel}/codes/{code} { allow read: if konto(); allow update: if konto() || admin(); allow create, delete: if admin(); }
  }
}
```

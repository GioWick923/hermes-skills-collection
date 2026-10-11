# Oracle Cloud: extraer OCIDs vía consola SPA (caso validado 2026-08-20)

Flujo validado para obtener Tenancy OCID y User OCID de Oracle Cloud Free Tier
cuando el navegador controlado no comparte la sesión del usuario pero sí logró
autenticarse (o el usuario ya hizo login una vez).

## Trucos clave de Oracle

- El iframe del contenido es `#sandbox-maui-preact-container` (same-origin).
- **Tenancy OCID = Compartment OCID del compartimiento raíz.** Ir a
  `https://cloud.oracle.com/identity/compartments?region=<región>` y leer el OCID
  del compartimiento "root". No hace falta buscar la página de tenancy.
- **User OCID** está en My profile:
  `https://cloud.oracle.com/identity/domains/my-profile?region=<región>`
  dentro del iframe, sección "User information → OCID".
- El dominio de identidad real es `Default`, NO el nombre de usuario. La URL
  `.../domains/armangio91/api-keys` da "Resource Not Found"; usar
  `.../domains/Default/...` o la URL de my-profile.
- Las API keys se ven en My profile → "Tokens and keys" → "API keys".
  Si la lista dice "No items to display" → la key NO se registró (solo se generó
  el par en disco). Falta "Add API key" → pegar la pública → "Add".

## Pasos exactos (browser_exec)

1. `new_tab("https://cloud.oracle.com")` — si el usuario ya hizo login una vez en
   el navegador controlado, la sesión persiste. Confirmar: título "Home | Oracle
   Cloud Infrastructure" (no página de login).
2. `goto_url("https://cloud.oracle.com/identity/compartments?region=<región>")`,
   esperar 6-8s, luego JS:
   ```js
   const f = document.getElementById('sandbox-maui-preact-container');
   f.contentDocument.body.innerText;  // contiene "ocid1.tenancy.oc1..aaaa..."
   ```
3. Para user OCID: `goto_url(".../identity/domains/my-profile?...")`, esperar 6-8s,
   walker de Shadow DOM (el OCID aparece dos veces: con sufijo "CopyPrefixFirst"
   y limpio).

## Config OCI (después de tener los OCIDs)

`~/.oci/config`:
```ini
[DEFAULT]
user=ocid1.user.oc1..<USER>
fingerprint=<md5 de la clave pública, 2:2:2...>
tenancy=ocid1.tenancy.oc1..<TENANCY>
region=mx-queretaro-1   # u otra
key_file=C:/Users/<USER>/.oci/oci_api_key_private.pem
```

Fingerprint: `openssl rsa -pubout -in key.pem | openssl rsa -pubin -outform DER | openssl md5 -c`

Test auth (Python):
```python
import oci
cfg = oci.config.from_file('C:/Users/<USER>/.oci/config')
oci.identity.IdentityClient(cfg).get_tenancy(cfg['tenancy'])
# → ServiceError 401 si el fingerprint no coincide con la key REGISTRADA en Oracle
```

## Pitfall de 401

401 NotAuthenticated casi siempre = la key pública registrada en Oracle NO
corresponde al fingerprint/privada local. Causas vistas:
- Se generaron DOS pares (el usuario pegó dos públicas distintas); la privada
  local corresponde a una, pero Oracle tiene registrada la otra.
- La key se generó pero nunca se agregó a la consola (lista vacía).
Fix: ver en consola el fingerprint REAL de la key registrada y usarlo, o re-agregar
la key con la pública que corresponde a la privada local.

## Región vista

El usuario usó `mx-queretaro-1` (Mexico Central). El compartimiento raíz era
`armangio91 (root)`, usuario `ArmandoGiovanni Baez` (`armangio91@gmail.com`).

# Oracle Cloud Free Tier — detalles de la sesión (2026-08)

## Estado Always Free (jun-2026)
- **ARM Ampere A1 reducido**: 2 OCPUs + 12GB RAM (antes 4 OCPUs + 24GB). Cambio
  silencioso el 12-jun-2026. Instancias creadas con el viejo 4/24 deben redimensionarse
  a 2/12 para seguir Always Free.
- **x86 e2.micro**: 1 OCPU + 1GB RAM — sin problemas de capacidad, entra al instante.
- 200GB boot volume total incluido; **1 sola instancia ARM** por tenancy.
- $300 crédito trial por 30 días (servicios pagos); expira y quedan los Always Free.
- 1 cuenta por persona; cuentas inactivas 30+ días pueden suspenderse.
- "Always Free Eligible" debe aparecer en el shape — si no, cobra.

## Requisitos de registro (los que más fallan)
- Tarjeta física Visa/Mastercard (virtuales/prepago = rechazo alto). Solo verificación,
  no cobra.
- Dirección EXACTA de la tarjeta, en inglés/romanizada. Desajuste = fallo.
- Red de casa SIN VPN/proxy (IP debe coincidir con la dirección).
- Incógnito ayuda. Reintentos repetidos del mismo dispositivo en ventana corta
  aumentan el score de riesgo → esperar 24h.

## Regiones (Home Region no cambia después)
| Público | Región recomendada |
|---|---|
| Europa | Frankfurt (estable), London, Amsterdam |
| USA | Phoenix (más capacidad), Ashburn |
| Asia | Tokyo/Osaka |

## Errores de capacidad (verificados en sesión)
- `Out of capacity for shape VM.Standard.A1.Flex in availability domain AD-1`
- `... in availability domain AD-1 and fault domain FD-3. Try creating the instance
  without specifying a fault domain`
- Soluciones en orden: (1) cambiar **Availability Domain** a AD-2/AD-3; (2) quitar
  fault domain ("Create instance without specifying a fault domain"); (3) cambiar de
  región; (4) reintentar en oleadas (madrugada, cada 10-15 min).
- **AD ≠ FD**: Availability Domain = "edificio", Fault Domain = "piso". Cambiar el
  piso no arregla el edificio lleno.

## Laberinto de la UI (verificado en sesión)
- "Select existing virtual cloud network" es el default → subnet vacío → bloqueado.
  Cambiar a **"Create new virtual cloud network"** + **"Create new public subnet"**.
- **Public IPv4 address = No / switch gris**: la IP pública solo se asigna en subnet
  pública. Subnet privada = switch deshabilitado. Recrear con public subnet.
- Boot volume default 46.6GB → subir a 200GB (gratis).
- Oracle Cloud Agent: dejar defaults (Custom Logs/Compute Monitoring/Cloud Guard Enabled
  son gratis y útiles).

## Costos reales si se pasa del free (Daytona vs Oracle)
- Daytona: $200 crédito + 5GB storage gratis; vCPU $0.0504/h, RAM $0.0162/GiB-h,
  storage $0.000108/GiB-h. Con 8GB RAM 24/7 ≈ $133/mes → los $200 duran ~1.5 meses.
  El video "gratis e infinita" es clickbait.
- Oracle: no cobra mientras estés dentro de Always Free. Recomendado: alerta de
  presupuesto $1 para avisar si algo se sale.

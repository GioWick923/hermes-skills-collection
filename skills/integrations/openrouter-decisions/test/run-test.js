import { decide } from "./openrouter-decisions.js";

const state = {
  message: "Necesito ayuda urgente: mi API cayó en producción y los clientes no pueden pagar.",
  channel: "support",
  userTier: "enterprise",
};

const questions = [
  { id: "is_urgent", type: "noul", instructions: "¿Es este un caso que requiere respuesta inmediata?", criteria: { true: "requiere acción ya", false: "puede esperar" } },
  { id: "route_to", type: "choice", instructions: "¿A qué equipo debe enrutarse este ticket?", criteria: { billing: "problemas de pago", infra: "caída de servicios", account: "gestión de cuenta" } },
  { id: "severity", type: "score", instructions: "Qué tan grave es en una rúbrica de 3 niveles", criteria: ["low", "mid", "high"] },
];

const res = await decide({ state, questions });
console.log(JSON.stringify(res, null, 2));

Quiero que actúes como PRINCIPAL ENGINEER / STAFF+ ENGINEER con autonomía técnica real y construyas directamente en el repositorio un prototipo avanzado, reusable y técnicamente sólido de un producto B2B llamado provisionalmente FREIGHT AUDIT.

NO quiero solamente una propuesta de arquitectura, pseudocódigo, snippets ni recomendaciones.

QUIERO QUE IMPLEMENTES.

Tenés permiso para invertir mucho trabajo de ingeniería en esta sesión. El costo marginal de sobreprogramar HOY es muy bajo, por lo que NO optimices por hacer el mínimo código posible.

Sin embargo, hay una distinción CRÍTICA:

- Sobreprogramar infraestructura reusable, generalidad, corrección, auditabilidad, tests, tooling, importación, trazabilidad y robustez: SÍ.
- Sobreprogramar supuestos particulares del dominio que todavía no verificamos con clientes reales: NO.

============================================================ 0. LEÉ ESTO ANTES DE TOMAR CUALQUIER DECISIÓN TÉCNICA
============================================================

Yo conozco mejor que vos:

- qué problema comercial quiero resolver;
- qué riesgos quiero evitar;
- qué propiedades tiene que conservar el producto;
- qué tipo de producto NO quiero construir;
- por qué estamos construyéndolo.

Vos probablemente podés decidir mejor que yo:

- arquitectura;
- stack;
- lenguaje;
- librerías;
- estructura del repositorio;
- algoritmos;
- patrones;
- modelo interno;
- estrategia de persistencia;
- formato de reglas;
- estructura de tests;
- generación de reportes;
- packaging;
- UI;
- orden de implementación;
- herramientas auxiliares.

Por eso:

TRATÁ COMO VINCULANTES LOS OBJETIVOS, INVARIANTES, RESTRICCIONES DE NEGOCIO Y CRITERIOS DE ÉXITO.

TRATÁ LAS DECISIONES TÉCNICAS QUE YO MENCIONE COMO SUGERENCIAS, NO COMO DOGMAS, SALVO QUE EXPLÍCITAMENTE DIGA QUE SON UNA RESTRICCIÓN DEL PRODUCTO.

Tu trabajo NO es obedecer mecánicamente una especificación técnica.

Tu trabajo es entender profundamente QUÉ PRODUCTO QUEREMOS LOGRAR Y ELEGIR EL MEJOR CAMINO TÉCNICO PARA LLEGAR A ÉL.

Si encontrás una arquitectura, stack, representación matemática, librería o enfoque sustancialmente mejor que algo sugerido en este prompt:

USALO.

No me pidas permiso por decisiones técnicas ordinarias.

Si una sugerencia mía entra en conflicto con el objetivo superior:

1. identificá mentalmente la tensión;
2. elegí la alternativa que mejor cumpla el objetivo;
3. implementala;
4. documentá brevemente al final por qué te apartaste de la sugerencia inicial.

NO cambies los fines para simplificar la implementación.

============================================================

1. # PROPÓSITO REAL DEL PRODUCTO

El producto apunta inicialmente a empresas argentinas que:

- contratan transporte terrestre tercerizado;
- reciben liquidaciones/facturas de transportistas;
- poseen algún acuerdo, tarifario o esquema comercial que determina cuánto debería cobrarse;
- tienen viajes, remitos, despachos u otros hechos operativos contra los cuales verificar lo liquidado;
- pagan o aprueban esos cargos;
- actualmente realizan algún control administrativo, manual, por Excel, ERP, TMS u otros medios.

Nuestro beachhead comercial inicial probablemente sean fabricantes medianos regionales, inicialmente con especial interés en pinturas/revestimientos.

PERO ESTO ES MUY IMPORTANTE:

EL MOTOR NO DEBE SER UN MOTOR PARA PINTURAS.

EL MOTOR NO DEBE SER UN MOTOR PARA RESOL.

EL MOTOR NO DEBE SER UN MOTOR PARA EL LITORAL.

EL MOTOR NO DEBE SER UN MOTOR PARA UN TRANSPORTISTA PARTICULAR.

EL MOTOR NO DEBE SER UN MOTOR PARA FADEEAC.

EL MOTOR NO DEBE SER UN MOTOR PARA UNA FORMA PARTICULAR DE FACTURAR.

La vertical inicial sirve para vender y aprender.

La arquitectura debe representar un problema más abstracto:

DATOS OPERATIVOS REALES

- REGLAS COMERCIALES VERSIONADAS
- CARGOS REALMENTE LIQUIDADOS
- # EVIDENCIA DISPONIBLE
  RECONSTRUCCIÓN DETERMINISTA DE QUÉ DEBERÍA HABERSE COBRADO
- COMPARACIÓN
- EXPLICACIÓN
- CLASIFICACIÓN DE CERTEZA
- DECISIÓN HUMANA FINAL.

Ésa es la esencia.

============================================================ 2. QUÉ VALOR VENDE EL PRODUCTO
============================================================

No vende dashboards.

No vende IA.

No vende tracking.

No vende GPS.

No vende routing.

No vende automatización por sí misma.

No vende "digitalización".

No vende simplemente detectar duplicados.

El valor consiste en poder responder, para cada cargo:

¿ESTE IMPORTE ESTÁ RESPALDADO POR EL ACUERDO Y LOS HECHOS DISPONIBLES?

Y si no lo está:

¿POR QUÉ?

La aplicación debe poder demostrar exactamente:

- qué información recibió;
- qué regla contractual/tarifaria aplicó;
- qué versión de esa regla era vigente;
- qué hechos operativos utilizó;
- qué cálculo realizó;
- qué evidencia encontró;
- qué evidencia faltó;
- qué cobró el transportista;
- qué esperaba el motor;
- qué diferencia existe;
- qué nivel de certeza tenemos;
- qué intervención humana ocurrió después.

Queremos convertir un control administrativo difícil de reproducir en una verificación:

DETERMINISTA

- TRAZABLE
- REPRODUCIBLE
- EXPLICABLE
- AUDITABLE.

============================================================ 3. OBJETIVO COMERCIAL QUE DEBE GUIAR LA ARQUITECTURA
============================================================

El producto sólo tiene sentido económicamente si incorporar un nuevo cliente tiende hacia:

CONFIGURAR DATOS

- CONFIGURAR REGLAS
- CONFIGURAR FORMATOS
- CONFIGURAR EVIDENCIAS

y NO hacia:

ESCRIBIR UN NUEVO PROGRAMA PARA CADA CLIENTE.

El criterio arquitectónico central es:

CLIENTE NUEVO ≈ NUEVA CONFIGURACIÓN.

NO:

CLIENTE NUEVO ≈ NUEVO CÓDIGO.

Naturalmente puede ocurrir que un cliente revele una abstracción genuinamente nueva que merezca ampliar el producto.

Eso está bien.

Lo que NO queremos es:

if client == "RESOL"
if client == "ClienteB"
if carrier == "TransportistaX"

ni equivalentes ocultos de esa práctica.

Si para incorporar una empresa normal del ICP tenemos que programar durante días lógica exclusiva para ella, el modelo de negocio empieza a convertirse en consultoría custom.

La arquitectura tiene que combatir activamente ese riesgo.

============================================================ 4. EL PRODUCTO DEBE SER AGNÓSTICO
============================================================

AGNÓSTICO NO significa abstracto hasta resultar inútil.

Significa que las diferencias entre clientes se expresan primordialmente como DATOS Y CONFIGURACIÓN.

El sistema debe ser, en la medida razonable, agnóstico respecto de:

- empresa;
- transportista;
- industria del cargador;
- provincia;
- localidad;
- rutas;
- cantidad de depósitos;
- terminología de columnas;
- nombres de conceptos;
- estructura de Excel;
- estructura de CSV;
- identificadores usados;
- fórmulas tarifarias;
- moneda;
- unidad de tarifa;
- factor volumétrico;
- indexador;
- adicionales;
- reglas de espera;
- reglas de redespacho;
- requisitos de evidencia;
- vigencias;
- tolerancias;
- mínimos;
- máximos;
- escalas;
- zonas;
- tipos de vehículo;
- peso;
- volumen;
- pallets;
- bultos;
- kilometraje;
- combinaciones de variables.

Argentina es el mercado inicial.

Por lo tanto, manejar bien:

- ARS;
- formatos numéricos argentinos;
- fechas locales;
- Excel real de empresas argentinas;
- nombres y estructuras imperfectas;

es muy importante.

Pero no diseñes el dominio de modo tal que conceptualmente sólo pueda funcionar en Argentina.

============================================================ 5. NO INVENTES EL DOMINIO
============================================================

Esta restricción es CRÍTICA.

Todavía NO conocemos suficientemente los acuerdos y workflows reales de nuestros primeros clientes.

Por lo tanto:

NO hardcodear supuestas prácticas "normales" de transporte.

Ejemplos de cosas que NO debés asumir:

- que el aforo siempre sea m³ × 250;
- que sea m³ × 333;
- que exista aforo;
- que se use FADEEAC;
- que se use IPC;
- que los aumentos sean mensuales;
- que exista combustible como adicional;
- que las estadías empiecen a 120 minutos;
- que una estadía requiera firma manuscrita;
- que un POD sea siempre obligatorio;
- que una reentrega tenga precio fijo;
- que mismo remito dos veces implique duplicación;
- que factura y liquidación sean el mismo documento;
- que un viaje tenga un único cargo;
- que un remito represente necesariamente un único viaje;
- que una factura contenga el detalle necesario;
- que determinado adicional sea legítimo o ilegítimo por defecto.

Si un acuerdo usa una regla:

REPRESENTALA.

Si no la usa:

NO DEBE EXISTIR PARA ESE ACUERDO.

Ejemplo incorrecto:

factorVolumetrico = 333

Ejemplo correcto:

el acuerdo puede contener opcionalmente una regla de peso facturable basada en volumen cuyo factor sea un parámetro versionado.

Ejemplo incorrecto:

"FADEEAC es el índice tarifario".

Ejemplo correcto:

una regla versionada puede tomar un factor de actualización documental explícitamente cargado.

Ejemplo incorrecto:

"sin firma, estadía inválida".

Ejemplo correcto:

el acuerdo puede declarar qué evidencia es requerida para considerar determinado concepto suficientemente respaldado.

Cuando desconozcamos una práctica real:

NO INVENTES UNA.

Creá una abstracción configurable si existe justificación suficiente.

Si ni siquiera sabemos todavía si merece una abstracción:

documentá la limitación y evitá cristalizar una suposición prematura.

============================================================ 6. EL SISTEMA NO ES UN JUEZ AUTOMÁTICO
============================================================

Queremos automatizar aquello que sea objetivamente determinable.

No queremos fabricar certeza.

Existen cuatro estados conceptuales fundamentales.

Podés cambiar sus nombres internos si encontrás una representación mejor, pero la semántica debe conservarse.

PASS

La información disponible permite determinar que el cargo coincide con lo esperado dentro de las reglas/tolerancias configuradas.

FAIL

La información disponible permite determinar que existe una discrepancia objetiva.

REVIEW

Existe una cuestión que necesita revisión humana.

Por ejemplo:

- evidencia faltante para un cargo potencialmente válido;
- matching ambiguo;
- posible duplicado;
- clasificación de concepto dudosa;
- excepción que requiere confirmación.

UNDETERMINABLE

No existe suficiente información para calcular o adjudicar correctamente el caso.

Por ejemplo:

- no sabemos qué versión tarifaria correspondía;
- existen dos reglas incompatibles simultáneamente aplicables;
- falta un dato esencial del viaje;
- el acuerdo disponible no define el caso.

PRINCIPIO ABSOLUTO:

REVIEW ≠ AHORRO.

UNDETERMINABLE ≠ AHORRO.

FALTA DE EVIDENCIA ≠ CARGO FALSO.

SOSPECHA ≠ DISCREPANCIA CONFIRMADA.

El producto debe ser extremadamente conservador al convertir algo en una diferencia económica confirmada.

============================================================ 7. EL HUMANO CONSERVA LA AUTORIDAD FINAL
============================================================

El motor produce una conclusión técnica según reglas, datos y evidencia.

El humano puede:

- aprobar;
- rechazar;
- solicitar más información;
- aceptar una excepción;
- ignorar;
- añadir evidencia;
- documentar una resolución.

Pero:

ENGINE FINDING

y

HUMAN DECISION

deben ser entidades conceptualmente distintas.

Una decisión posterior de una persona NO debe reescribir silenciosamente lo que el motor había determinado.

Queremos poder reconstruir:

"El motor marcó REVIEW por X.

Luego Juan Pérez confirmó Y con evidencia Z.

La resolución final fue APPROVED."

La historia importa.

============================================================ 8. REPRODUCIBILIDAD COMO PROPIEDAD FUNDAMENTAL
============================================================

Quiero poder volver dentro de seis meses a una auditoría y responder:

¿Por qué el sistema concluyó esto?

Necesitamos poder reconstruir:

INPUTS

- VERSIONES
- CONFIGURACIÓN
- REGLAS
- MAPPINGS
- EVIDENCIA
- VERSIÓN DEL MOTOR
- RESULTADO ORIGINAL.

Si nada cambia:

MISMO INPUT NORMALIZADO

- MISMA CONFIGURACIÓN
- MISMA VERSIÓN DEL MOTOR

debe producir:

MISMO RESULTADO LÓGICO.

El núcleo no debería depender accidentalmente de:

- hora actual;
- orden accidental de filas;
- estado global;
- IDs aleatorios;
- red;
- servicios externos;
- floating point inestable;
- concurrencia no determinista;
- locale del sistema operativo.

Separá claramente metadata incidental de resultado determinista.

============================================================ 9. EXPLICABILIDAD: NO ES UNA FEATURE SECUNDARIA
============================================================

La explicación es una parte CENTRAL del producto.

No quiero solamente:

FAIL: diferencia $50.000.

Quiero poder inspeccionar algo conceptualmente equivalente a:

Viaje:
R-45102

Acuerdo:
Transportista X

Versión:
2026-09-v3

Regla:
R-014

Datos utilizados:
peso = 2800 kg
destino = Rosario

Lookup:
Santo Tomé -> Rosario
180 ARS/kg

Cálculo:
2800 × 180 = 504000

Regla adicional:
5 %

Cálculo:
504000 × 0.05 = 25200

Esperado:
529200

Facturado:
579200

Diferencia:
50000

Estado:
FAIL

La explicación humana debe derivarse de una TRAZA ESTRUCTURADA DE CÁLCULO.

No quiero:

lógica por un lado

- texto explicativo artesanal por otro.

La explicación debe ser producto directo de la ejecución real.

============================================================ 10. PRECISIÓN MONETARIA
============================================================

Este software puede intervenir en decisiones económicas.

No aceptar errores silenciosos de precisión.

Elegí la estrategia adecuada para:

- dinero;
- decimales;
- porcentajes;
- divisiones;
- tasas;
- redondeos;
- monedas;
- escalas.

No quiero bugs estilo:

0.1 + 0.2 != 0.3

afectando resultados.

Todo redondeo relevante debe ser EXPLÍCITO y, si corresponde, configurable.

No escondas una política de redondeo dentro de implementación incidental.

============================================================ 11. MODELO DE DOMINIO
============================================================

Diseñá vos el mejor modelo.

Como orientación, sabemos que conceptualmente existen cosas semejantes a:

Carrier
Agreement
AgreementVersion
Shipment
Remittance / Dispatch
Settlement
ActualCharge
ExpectedCharge
Evidence
Rule
AuditFinding
AuditRun
HumanDecision
SourceDocument
ImportMapping

Pero NO estás obligado a usar exactamente estas entidades ni estos nombres.

Buscá un modelo que sea:

- entendible;
- extensible;
- auditable;
- estable;
- reusable;
- poco acoplado;
- explícito.

Debe poder representar atributos comunes como:

- referencia;
- remito;
- fecha;
- origen;
- destino;
- peso;
- volumen;
- pallets;
- bultos;
- vehículo;

sin obligarnos a modificar código cada vez que aparece una variable nueva legítima.

Necesitamos algún mecanismo sano de atributos extensibles.

No conviertas todo en un Map<string, any> sin estructura.

Buscá equilibrio entre:

TIPADO

y

EXTENSIBILIDAD.

============================================================ 12. MOTOR DE REGLAS
============================================================

Éste probablemente sea uno de los activos técnicos centrales.

Necesitamos representar acuerdos comerciales versionados sin escribir código client-specific.

Elegí la representación que consideres mejor.

Puede ser:

- DSL declarativa;
- AST;
- esquema de reglas;
- expresión segura;
- combinación de primitives;
- alguna solución existente;
- otro enfoque mejor que encuentres.

REQUISITOS:

- auditable;
- serializable;
- versionable;
- seguro;
- determinista;
- sin ejecución arbitraria peligrosa;
- suficientemente expresivo;
- comprensible;
- testeable.

NO quiero un lenguaje Turing-completo porque sí.

Preferimos un conjunto limitado y bien definido de primitives que cubran reglas reales.

Ejemplos de primitives que probablemente sean útiles:

- importe fijo;
- tarifa por unidad;
- mínimo;
- máximo;
- porcentaje;
- escalas;
- rangos;
- tabla de lookup;
- zona;
- origen/destino;
- vehículo;
- condición;
- vigencia;
- adicional;
- factor;
- fórmula compuesta;
- redondeo;
- requisito documental;
- tolerancia.

Pero NO asumas que esta lista es perfecta ni exhaustiva.

Diseñá mejores primitives si corresponde.

============================================================ 13. VERSIONES Y VIGENCIA
============================================================

Los acuerdos cambian.

No queremos sobrescribir el pasado.

Un mismo acuerdo puede tener:

v1
v2
v3...

y cada una puede aplicar según criterios explícitos.

Ejemplo simple:

v1:
01/01/2026–30/06/2026

v2:
01/07/2026–31/08/2026

v3:
desde 01/09/2026

Un viaje del 15/07 debería poder seleccionar v2.

Pero incluso la fecha relevante puede variar según acuerdo.

Quizás un cliente use:

fecha de despacho

otro:

fecha de prestación

otro:

fecha de carga

Por eso tampoco hardcodees innecesariamente qué evento gobierna la vigencia.

Si dos versiones son simultáneamente válidas y no existe criterio para resolverlo:

NO selecciones una arbitrariamente.

La ambigüedad tiene que emerger.

============================================================ 14. IMPORTACIÓN DE DATOS REALES
============================================================

Ésta probablemente sea otra de las partes más importantes comercialmente.

Los clientes van a entregar archivos feos.

No archivos que coinciden con nuestro schema.

Pueden existir:

- XLSX;
- XLS;
- CSV;
- varias hojas;
- headers extraños;
- columnas irrelevantes;
- columnas faltantes;
- distintos separadores;
- números con coma decimal;
- números con punto de miles;
- fechas como texto;
- referencias con ceros iniciales;
- conceptos escritos de varias maneras;
- archivos reordenados.

Necesitamos un sistema reusable de importación y mapping.

Algo conceptualmente como:

"Numero Rem."
→ shipment.reference

"Peso KG"
→ shipment.weightKg

"Fecha Despacho"
→ shipment.serviceDate

El mapping debe poder guardarse y reutilizarse para la próxima importación del mismo origen.

Debe existir alguna estrategia explícita para:

- preview;
- selección de sheet;
- headers;
- tipos;
- parsing;
- normalización;
- errores;
- warnings;
- filas rechazadas;
- filas aceptadas;
- conversiones.

NO hagas coerciones peligrosas silenciosas.

Si un dato es ambiguo:

exponelo.

============================================================ 15. NORMALIZACIÓN DE CONCEPTOS
============================================================

Los transportistas pueden llamar a un mismo concepto:

"Espera"
"Estadía"
"Tiempo descarga"
"Demora"

o pueden significar cosas distintas usando palabras parecidas.

Necesitamos poder mapear:

concepto externo
→ concepto canónico/configurado

sin asumir equivalencias globales.

El mapping tiene que poder ser:

- específico de fuente;
- explícito;
- reusable;
- auditable.

NO uses IA para inferirlo silenciosamente.

Más adelante podría existir asistencia inteligente.

El núcleo actual debe poder funcionar sin ella.

============================================================ 16. MATCHING ENTRE MUNDOS
============================================================

Tenemos al menos dos universos:

OPERACIÓN REAL

y

COBRO DEL TRANSPORTISTA.

Necesitamos relacionarlos.

El matching inicial debe ser CONSERVADOR.

Preferir identificadores explícitos y reglas configurables.

Puede existir:

1 viaje → 1 cargo
1 viaje → N cargos
N viajes → 1 cargo consolidado
otras relaciones.

No hardcodees cardinalidad innecesariamente.

No hagas fuzzy matching silencioso que pueda asociar dinero al viaje incorrecto.

Si existen varios candidatos:

REVIEW.

Si no existe ninguno:

REVIEW o UNDETERMINABLE según el caso.

Puede ser útil implementar:

- aliases;
- claves compuestas;
- mappings explícitos;
- estrategias de matching configurables;
- score sólo como sugerencia, nunca como unión silenciosa.

Elegí una arquitectura que permita evolucionar.

============================================================ 17. EVIDENCIA
============================================================

La legitimidad de un cargo puede depender de evidencia.

Ejemplos posibles:

- POD;
- remito conformado;
- autorización;
- timestamp;
- email;
- documento;
- evento del sistema;
- observación.

Pero NO existe un universal a priori.

Una regla puede declarar algo conceptualmente como:

Para cobrar concepto X se requiere evidencia de tipo A o B.

Si falta:

NO implica automáticamente FAIL.

Probablemente implique REVIEW.

El motor debe poder explicar:

"El cargo podría ser válido, pero según la configuración falta evidencia requerida X."

============================================================ 18. CÁLCULO ESPERADO VS CARGO REAL
============================================================

El núcleo debe poder:

1. identificar la operación;
2. determinar acuerdo;
3. determinar versión aplicable;
4. ejecutar reglas;
5. construir cargos esperados;
6. relacionarlos con cargos reales;
7. comparar;
8. clasificar;
9. explicar.

Casos relevantes:

- coincide;
- importe diferente;
- tarifa equivocada;
- regla equivocada;
- versión equivocada;
- cargo esperado ausente;
- cargo real inesperado;
- evidencia faltante;
- referencia inexistente;
- posible duplicación;
- varias líneas legítimas para mismo viaje;
- ambigüedad;
- dato faltante;
- regla no definida.

No conviertas automáticamente:

"cargo inesperado"

en:

"cargo incorrecto".

La configuración puede no cubrir el universo completo.

============================================================ 19. DUPLICADOS
============================================================

Quiero especial cuidado acá.

"Mismo remito aparece dos veces"

NO significa necesariamente:

"cobro duplicado".

Podría representar:

- dos servicios;
- dos conceptos;
- segunda entrega;
- devolución;
- otra relación legítima.

Por defecto:

DETECTAR CANDIDATO

≠

DICTAMINAR DUPLICADO.

Sólo producir discrepancia confirmada si reglas/datos permiten demostrarlo.

============================================================ 20. RESULTADOS ECONÓMICOS
============================================================

Necesitamos separar claramente magnitudes.

Por ejemplo:

TOTAL FACTURADO

TOTAL DETERMINABLE

TOTAL PASS

DIFERENCIA DETERMINADA

IMPORTE EN REVIEW

IMPORTE UNDETERMINABLE

COBERTURA DE AUDITORÍA

No necesariamente uses exactamente esas métricas si encontrás mejores definiciones.

Pero la idea esencial debe preservarse.

Bajo ninguna circunstancia sumar:

REVIEW + UNDETERMINABLE

como:

AHORRO.

Incluso para FAIL, documentá con precisión qué significa económicamente.

============================================================ 21. SALIDA OPERATIVA Y EJECUTIVA
============================================================

El sistema debería poder producir una salida útil para dos perfiles diferentes.

A. ADMINISTRATIVO / OPERATIVO

Necesita detalle granular:

- viaje/remito;
- concepto;
- facturado;
- esperado;
- diferencia;
- estado;
- regla;
- motivo;
- evidencia;
- observación;
- resolución.

Preferentemente exportable a un formato tabular cómodo para trabajar.

XLSX probablemente sea muy útil.

B. GERENCIA / FINANZAS

Necesita resumen:

- cuánto se analizó;
- cuánto pudo determinarse;
- cuántas discrepancias objetivas;
- importe asociado;
- cuánto requiere revisión;
- cuánto no pudo determinarse;
- principales causas;
- cobertura.

Probablemente:

HTML imprimible / PDF.

Elegí la implementación que dé mayor robustez.

NO sacrifiques arquitectura por producir un PDF bonito.

============================================================ 22. INTERFAZ
============================================================

No necesitamos una plataforma SaaS completa todavía.

Pero hoy tenemos capacidad abundante de implementación.

Por eso una interfaz local de demostración puede ser MUY útil si no perjudica el núcleo.

La UI ideal debería mostrar el workflow real:

Nueva auditoría
→ importar operación
→ importar liquidación
→ seleccionar/configurar acuerdo
→ cargar evidencia si existe
→ validar mappings
→ ejecutar
→ resumen
→ findings
→ explicación
→ resolver casos humanos
→ exportar.

No necesito:

- login;
- signup;
- Stripe;
- Mercado Pago;
- roles complejos;
- organizaciones;
- onboarding SaaS;
- emails;
- notificaciones;
- analytics;
- mobile app;
- animaciones.

Quiero una UI profesional, sobria y clara.

Pero:

CORE CORRECTO > UI BONITA.

============================================================ 23. LOCAL-FIRST / OFFLINE / PRIVACIDAD
============================================================

Ésta es una restricción fuerte del producto.

Uno de nuestros objetivos es reducir dependencia de servicios externos críticos.

La lógica de auditoría debe poder funcionar SIN INTERNET.

Los datos confidenciales de un cliente NO deberían necesitar salir de su equipo para producir el resultado.

No quiero que el core dependa de:

- APIs externas;
- cloud;
- servicios de IA;
- Google;
- Meta;
- ARCA;
- bancos;
- servicios de terceros;
- jobs remotos;
- webhooks;
- servidores para realizar el cálculo.

Esto NO significa que toda futura versión comercial tenga prohibido cualquier servidor.

Podríamos usar eventualmente un servidor para:

- licencia;
- actualización;
- distribución;
- colaboración opcional.

Pero:

EL CAMINO CRÍTICO DE AUDITORÍA DEBE PODER FUNCIONAR LOCALMENTE.

Si el servidor cae:

no debería desaparecer nuestra capacidad matemática de auditar un lote.

============================================================ 24. PORTABILIDAD Y DESPLIEGUE
============================================================

Pensá en el usuario final real.

Muchas empresas argentinas probablemente trabajen en Windows con Excel.

El fundador desarrolla principalmente en un entorno moderno de desarrollo y necesita mantener el código solo.

Por lo tanto, al elegir stack contemplá:

- mantenibilidad por un programador;
- facilidad de debugging;
- packaging;
- instalación;
- Windows;
- desarrollo en Linux;
- offline;
- updates;
- performance;
- acceso a XLSX;
- generación de reportes;
- testabilidad;
- auditabilidad;
- posibilidad futura de tener UI web/local;
- posibilidad futura de evolucionar a producto comercial sin reescribir el core.

No elijas un stack solamente porque sea elegante para una demo.

Elegí uno que tenga sentido si dentro de dos años hay 20 clientes usando el producto.

============================================================ 25. STACK: TENÉS LIBERTAD
============================================================

NO estás obligado a usar:

- TypeScript;
- Python;
- Rust;
- React;
- SQLite;
- Electron;
- Tauri;
- Node;
- monorepo;
- ninguna tecnología específica.

Elegí vos.

PERO justificá la decisión contra LOS OBJETIVOS DEL PRODUCTO.

Algunos datos contextuales relevantes:

- el fundador es un programador independiente;
- su stack habitual incluye TypeScript/React;
- va a mantener el producto principalmente solo al principio;
- necesita velocidad de iteración;
- necesita auditar y entender su propio código;
- el motor requiere extrema testabilidad;
- necesitamos excelente manejo de archivos tabulares;
- queremos una eventual UI usable;
- queremos evitar una reescritura innecesaria cuando aparezca el primer cliente pago;
- clientes probablemente usen Windows;
- el fundador desarrolla en Linux.

No elijas TypeScript simplemente porque es conocido.

No elijas Python simplemente porque tiene Pandas.

No elijas Rust simplemente porque parece robusto.

Compará mentalmente las alternativas contra el propósito completo y elegí.

Si tiene sentido separar:

CORE EN X

- UI EN Y

podés hacerlo.

Pero evitá complejidad operativa innecesaria.

============================================================ 26. PERSISTENCIA
============================================================

Elegí el mecanismo apropiado.

Necesitamos eventualmente almacenar localmente:

- acuerdos;
- versiones;
- mappings;
- configuraciones;
- auditorías;
- findings;
- decisiones;
- hashes;
- provenance;
- evidencia referenciada;
- metadata.

Puede ser:

- SQLite;
- archivos versionados;
- ambos;
- otra solución.

Buscá:

- reproducibilidad;
- portabilidad;
- backups;
- inspectabilidad;
- migraciones;
- facilidad de soporte.

No conviertas prematuramente esto en arquitectura distribuida.

============================================================ 27. PROVENANCE
============================================================

Quiero saber de dónde salió cada dato relevante.

Idealmente, un valor normalizado pueda rastrearse hasta:

archivo
→ sheet
→ fila
→ columna

o equivalente.

Ejemplo:

pesoKg = 2800

source:
ViajesSeptiembre.xlsx
sheet "Despachos"
row 54
column "KG NETOS"

Esto puede ser extremadamente valioso cuando alguien pregunta:

"¿De dónde sacaste ese número?"

Diseñá una estrategia viable.

No necesariamente hace falta arrastrar provenance pesadísimo a absolutamente cada operación si produce un costo absurdo.

Pero tratá la trazabilidad de origen como propiedad importante.

============================================================ 28. SNAPSHOTS / HASHES / INTEGRIDAD
============================================================

Pensá cómo preservar evidencia de qué exactamente fue auditado.

Podría ser útil hashear:

- source documents;
- normalized datasets;
- agreement;
- rule configuration;
- mappings;
- engine version;
- audit result.

Elegí vos el esquema correcto.

Queremos poder detectar:

"El Excel fue reemplazado después."

No necesitamos blockchain.

Necesitamos integridad práctica y verificable.

============================================================ 29. DATASET DE DEMOSTRACIÓN
============================================================

Creá un dataset TOTALMENTE FICTICIO pero realista.

No quiero copiar tarifas reales de ninguna empresa.

Por ejemplo:

Empresa ficticia:
Pinturas Delta SA

Transportista ficticio:
Transporte Litoral SRL

Podés usar localidades reales argentinas.

Generá suficiente complejidad para probar generalidad.

Aproximadamente:

20–50 viajes

y suficientes cargos para representar:

- PASS;
- FAIL;
- REVIEW;
- UNDETERMINABLE;
- tarifa por unidad;
- mínimo;
- porcentaje;
- rango;
- zona;
- distintas vigencias;
- evidencia;
- adicional;
- referencia inexistente;
- posible duplicado;
- varios cargos legítimos del mismo viaje;
- error de importación;
- redondeo;
- ambigüedad tarifaria.

IMPORTANTE:

todos los supuestos del dataset son:

FICTICIOS.

Etiquetalos claramente.

No presentes esos ejemplos como prácticas del sector.

============================================================ 30. TESTS: QUIERO UNA INVERSIÓN MUY ALTA
============================================================

Tenemos oportunidad de sobreinvertir hoy.

USALA.

Quiero tests sustantivos.

No tests que sólo confirman getters.

Como mínimo investigá e implementá donde aporte valor:

- unit tests;
- integration tests;
- end-to-end;
- golden tests;
- property-based tests;
- fuzzing;
- malformed inputs;
- deterministic replay;
- serialization roundtrip;
- migration tests si hay persistencia;
- report generation tests.

Propiedades especialmente importantes:

A.

Mismos inputs normalizados

- misma configuración
- misma versión

→ mismo resultado.

B.

Reordenar filas que semánticamente representan lo mismo no debería alterar el resultado económico.

C.

Falta de evidencia no debe convertirse automáticamente en FAIL.

D.

REVIEW no debe contabilizarse como ahorro.

E.

UNDETERMINABLE no debe contabilizarse como ahorro.

F.

Dos versiones tarifarias ambiguas no deben resolverse silenciosamente.

G.

Un importe monetario no debe degradarse por floating point.

H.

Una regla inexistente no debe inventarse.

I.

Un concepto desconocido no debe clasificarse silenciosamente como uno conocido.

J.

Un matching ambiguo no debe resolverse automáticamente.

K.

Una decisión humana posterior no debe borrar el finding original.

L.

Cambiar una versión tarifaria NO debe cambiar auditorías históricas ya congeladas.

M.

Dos cargos con mismo remito no deben asumirse automáticamente duplicados.

N.

Errores de importación deben ser visibles.

============================================================ 31. ADVERSARIAL TESTING
============================================================

Después de que funcione:

TRATÁ DE ROMPER TU PROPIO SISTEMA.

Asumí que mañana alguien podría tomar una decisión de pago real basándose en esto.

Buscá especialmente casos donde pueda:

- inventar un FAIL;
- ocultar incertidumbre;
- utilizar tarifa incorrecta;
- seleccionar versión equivocada;
- duplicar montos;
- omitir cargos;
- asociar mal un viaje;
- perder precisión;
- interpretar mal números argentinos;
- confundir fecha;
- fallar por timezone;
- aceptar archivo corrupto;
- contar REVIEW como ahorro;
- contar UNDETERMINABLE como ahorro;
- cambiar resultado por orden de entrada;
- perder provenance;
- modificar silenciosamente pasado.

Cada bug encontrado:

1. reproducilo con test;
2. corregilo;
3. mantené el test.

============================================================ 32. GENERALIZACIÓN ADVERSARIAL
============================================================

Una vez construido el motor, quiero que pruebes explícitamente que NO está sobreajustado al dataset inicial.

Creá al menos tres acuerdos ficticios muy distintos.

EJEMPLO A

tarifa por kg

- mínimo
- adicional porcentual.

EJEMPLO B

importe fijo por combinación:

zona

- tipo de vehículo.

EJEMPLO C

tramos de peso

- cargo por pallet
- adicional que requiere evidencia.

Idealmente agregá uno aún más diferente si sirve para estresar el diseño.

OBJETIVO:

Incorporarlos cambiando CONFIGURACIÓN.

No lógica específica del core.

Si necesitás modificar el core:

preguntate si descubriste una abstracción general legítimamente faltante.

Si sí:

agregala de forma reusable.

Si no:

no contamines el core con excepción específica.

============================================================ 33. SEGUNDO CLIENTE COMO TEST ARQUITECTÓNICO
============================================================

Pensá constantemente en este escenario:

Cliente A ya funciona.

Mañana llega Cliente B.

Tiene:

- columnas distintas;
- transportista distinto;
- tarifario distinto;
- nombres de conceptos distintos;
- otra combinación de reglas;
- otro layout de Excel.

¿Cuánto código hay que escribir?

El objetivo ideal es:

POCO O NADA.

El esfuerzo debería concentrarse en:

- mapping;
- configuración;
- validación;
- carga de reglas;
- pruebas.

Éste es probablemente uno de los KPI técnicos más importantes.

============================================================ 34. PERFORMANCE
============================================================

No necesitamos hyperscale.

Pero tampoco quiero una arquitectura que accidentalmente no pueda procesar un cierre real.

Generá benchmarks razonables.

Por ejemplo:

10.000 viajes

50.000 cargos

y, si el diseño lo permite:

100.000 cargos.

Medí:

- tiempo;
- memoria;
- cuello de botella.

No sacrifiques claridad por optimizaciones inútiles.

Simplemente asegurate de no construir algo patológicamente lento.

============================================================ 35. OBSERVABILIDAD LOCAL
============================================================

Cuando algo falla necesito saber POR QUÉ.

Implementá errores útiles.

No:

"Error processing file".

Sí:

"Fila 84: campo fechaServicio contiene '31/13/2026', que no puede interpretarse con locale es-AR."

o equivalente.

Distinguir:

- error del archivo;
- error del mapping;
- error del acuerdo;
- ambigüedad;
- inconsistencia;
- bug interno.

No llenar la pantalla de stack traces para el usuario.

Pero conservar información técnica suficiente para debugging.

============================================================ 36. SEGURIDAD
============================================================

Procesamos información empresarial sensible.

La versión actual debe ser sobria.

No:

- telemetría oculta;
- analytics externos;
- código remoto;
- CDN obligatorio;
- eval;
- plugins arbitrarios inseguros;
- uploads invisibles;
- llamadas de red innecesarias.

Si la aplicación realiza cualquier llamada de red:

debe ser intencional, visible y no necesaria para auditar.

============================================================ 37. QUÉ NO CONSTRUIR TODAVÍA
============================================================

Salvo que descubras una razón arquitectónica extraordinariamente fuerte:

NO priorices:

- autenticación SaaS;
- organizaciones;
- permisos complejos;
- billing;
- Mercado Pago;
- Stripe;
- emails;
- WhatsApp;
- OCR general;
- LLM para leer contratos;
- integración automática con ERP;
- integración TMS;
- ARCA;
- bancos;
- tracking;
- GPS;
- optimización de rutas;
- driver app;
- app móvil;
- portal transportista;
- reclamos automáticos;
- pagos automáticos.

Nada de esto es necesario para validar el núcleo económico.

============================================================ 38. SOBRE IA / OCR
============================================================

El core debe ser completamente funcional SIN IA.

En el futuro podríamos usar IA como:

ASISTENTE

para:

- sugerir mappings;
- interpretar documentos;
- proponer reglas;
- detectar conceptos;
- resumir findings.

Pero una IA jamás debería convertir silenciosamente una inferencia probabilística en una conclusión contable determinista.

Si experimentás con alguna ayuda inteligente:

debe ser opcional y separada del núcleo confiable.

No es prioridad ahora.

============================================================ 39. REPORTES
============================================================

Quiero salida operativa reusable.

Probablemente tenga sentido producir:

audit.json

- auditoria.xlsx

- reporte ejecutivo HTML/PDF.

Pero elegí vos.

El XLSX debería ser realmente usable.

Por ejemplo, podría incluir:

Resumen
Hallazgos
Cálculos
Problemas de datos
Evidencia
Decisiones
Metadata

Las columnas de hallazgos podrían incluir:

referencia
remito
fecha
transportista
concepto
facturado
esperado
diferencia
estado
regla
versión
motivo
evidencia
observación

No estás obligado a exactamente esa estructura.

Optimízala.

============================================================ 40. CLI / AUTOMATIZACIÓN
============================================================

Aunque exista UI, quiero alguna manera reproducible y scriptable de correr auditorías.

Puede ser CLI, comando interno, API local o equivalente.

El objetivo es poder:

- automatizar tests;
- reproducir corridas;
- procesar fixtures;
- depurar;
- ejecutar sin UI.

Algo conceptualmente parecido a:

audit \
 --shipments viajes.xlsx \
 --settlement liquidacion.xlsx \
 --agreement tarifario.json \
 --mapping mapping.json \
 --out resultado/

Pero decidí vos la interfaz adecuada.

============================================================ 41. DOCUMENTACIÓN
============================================================

Documentá el sistema para que el fundador pueda entenderlo después.

Necesito documentación sobre:

- arquitectura;
- modelo;
- motor de reglas;
- semántica PASS/FAIL/REVIEW/UNDETERMINABLE;
- dinero;
- importación;
- mappings;
- matching;
- evidencia;
- versionado;
- reproducibilidad;
- provenance;
- reporting;
- cómo incorporar nuevo cliente;
- limitaciones;
- decisiones de stack;
- decisiones arquitectónicas importantes.

Especialmente:

FIRST_REAL_CLIENT.md

o equivalente.

Debe explicar qué hacer cuando mañana llegue el primer caso verdadero.

============================================================ 42. PRIMER CLIENTE REAL
============================================================

Diseñá el sistema pensando en este workflow:

1. recibimos ejemplos de archivos;
2. identificamos estructura;
3. creamos mapping;
4. entendemos el acuerdo;
5. representamos las reglas;
6. cliente confirma que nuestra representación refleja el acuerdo;
7. importamos un período que ellos YA controlaron;
8. corremos auditoría sin mirar inicialmente sus conclusiones;
9. comparamos;
10. medimos:

- diferencias nuevas;
- diferencias que ellos ya conocían;
- falsos positivos;
- casos indeterminados;
- tiempo humano nuestro;
- tiempo humano de ellos;
- porcentaje determinable;

11. decidimos si existe beneficio incremental real.

El software debe facilitar este experimento.

============================================================ 43. TODAVÍA NO ESTAMOS VALIDANDO QUE "AHORRE DINERO"
============================================================

No confundas corrección técnica con validación comercial.

Podemos construir un motor perfecto y descubrir que:

- los clientes ya controlan todo;
- los errores son raros;
- preparar datos cuesta demasiado;
- los acuerdos son demasiado ambiguos;
- falta evidencia;
- el volumen es chico;
- nadie paga por assurance;
- mantener reglas consume demasiadas horas.

Por eso:

NO diseñes marketing falso dentro del producto.

NO etiquetes arbitrariamente cualquier discrepancia como:

"ahorro".

El software debe ayudarnos a MEDIR si existe beneficio incremental.

============================================================ 44. MÉTRICAS QUE NOS INTERESA PODER MEDIR
============================================================

Sería valioso que la arquitectura permita calcular eventualmente:

- monto procesado;
- % determinable;
- % REVIEW;
- % UNDETERMINABLE;
- diferencias confirmadas;
- diferencias ya detectadas por cliente;
- nuevas diferencias;
- tiempo de preparación;
- tiempo de auditoría;
- tiempo de revisión humana;
- cantidad de excepciones;
- rules coverage;
- datos faltantes;
- frecuencia de override humano.

No hace falta construir una suite BI.

Simplemente no cierres la arquitectura a medir estas cosas.

============================================================ 45. NO CONFUNDAS CONFIGURABILIDAD CON UN MONSTRUO GENÉRICO
============================================================

Existe un riesgo inverso.

Por querer ser reusable podríamos construir un framework absurdamente abstracto.

NO hagas eso.

Queremos:

GENERALIDAD SUFICIENTE PARA CLIENTES REALES DEL PROBLEMA

NO:

UN FRAMEWORK UNIVERSAL PARA CUALQUIER CONTRATO DE LA HUMANIDAD.

Aplicá YAGNI cuando corresponda.

La prueba debe ser:

"¿Esta abstracción reduce razonablemente el código específico que necesitaremos para futuros clientes?"

Si no:

probablemente no la necesitemos.

============================================================ 46. NO SOBREINGENIERÍA DISTRIBUIDA
============================================================

Tenemos permiso para sobreinvertir en calidad.

Eso NO significa:

- microservicios;
- Kafka;
- Kubernetes;
- event sourcing complejo;
- CQRS porque sí;
- distributed consensus;
- arquitectura enterprise teatral.

La complejidad debe estar justificada por:

- corrección;
- auditabilidad;
- generalidad;
- mantenibilidad;
- reproducibilidad.

No por moda.

============================================================ 47. USABILIDAD
============================================================

Aunque el primer operador sea el fundador, diseñá pensando en que más adelante una administrativa de Pago a Proveedores o Logística debería poder usarlo.

No necesariamente ahora sin capacitación.

Pero evitá decisiones que obliguen para siempre a editar código.

Idealmente tareas recurrentes como:

- cambiar tarifario;
- importar nuevo período;
- mapear archivo;
- revisar finding;
- aportar evidencia;
- exportar;

deberían poder realizarse eventualmente desde UI/configuración.

No es obligatorio que absolutamente todo esté listo hoy.

============================================================ 48. DECISIONES TÉCNICAS: JERARQUÍA DE AUTORIDAD
============================================================

Usá esta jerarquía cuando haya tensiones:

NIVEL 1 — INNEGOCIABLE

Propósito del producto.

NIVEL 2 — INNEGOCIABLE

Corrección y semántica de certeza.

NIVEL 3 — MUY FUERTE

Auditabilidad, reproducibilidad, privacidad y bajo acoplamiento a servicios externos.

NIVEL 4 — MUY FUERTE

Reusabilidad entre clientes mediante configuración.

NIVEL 5 — IMPORTANTE

Mantenibilidad por fundador independiente.

NIVEL 6 — IMPORTANTE

Usabilidad real y velocidad para probar clientes.

NIVEL 7 — FLEXIBLE

Arquitectura concreta.

NIVEL 8 — FLEXIBLE

Lenguajes, frameworks y librerías.

NIVEL 9 — MUY FLEXIBLE

Carpetas, nombres, patrones y orden exacto de implementación.

Si una preferencia de nivel bajo perjudica un nivel alto:

SACRIFICÁ LA DE NIVEL BAJO.

============================================================ 49. ORDEN DE EJECUCIÓN
============================================================

Elegí vos el mejor orden.

Como orientación conceptual probablemente tenga sentido resolver primero:

- modelo;
- representación monetaria;
- reglas;
- cálculo;
- explicación;
- tests;
- fixtures;
- importación;
- matching;
- reporting;
- persistencia;
- UI.

Pero NO es obligatorio.

Lo que sí es obligatorio:

NO construir una UI bonita sobre un núcleo dudoso.

============================================================ 50. METODOLOGÍA DE TRABAJO
============================================================

No me entregues primero 5 páginas de propuesta esperando aprobación.

EMPEZÁ TRABAJANDO.

Podés hacer una evaluación arquitectónica breve internamente y luego implementar.

Trabajá directamente sobre el repositorio.

Creá archivos.

Instalá dependencias.

Implementá.

Ejecutá.

Probá.

Corregí.

Volvé a ejecutar.

Usá las herramientas disponibles.

No declares:

"debería funcionar"

si podés comprobarlo.

Quiero, según stack:

- typecheck/compile;
- lint;
- tests;
- build;
- ejecución del fixture;
- generación real de reportes;
- ejecución real de UI si existe.

============================================================ 51. NO TE DETENGAS POR UNA INCÓGNITA MENOR
============================================================

Si encontrás una decisión técnica razonable:

tomala.

Si encontrás una incógnita de negocio:

NO la inventes.

Modelala como:

- configuración;
- desconocido;
- limitación;
- punto a validar.

Sólo preguntame algo si realmente bloquea un objetivo fundamental y no existe una decisión reversible razonable.

============================================================ 52. REVISIÓN ADVERSARIAL FINAL
============================================================

Cuando creas que terminaste la primera versión:

NO TERMINASTE.

Hacé una segunda pasada como auditor hostil del propio producto.

Buscá:

- assumptions ocultos;
- hardcoding sectorial;
- hardcoding cliente;
- reglas arbitrarias;
- dinero impreciso;
- rounding silencioso;
- nondeterminismo;
- errores de vigencia;
- matching peligroso;
- estados mal clasificados;
- REVIEW contabilizado mal;
- pérdida de provenance;
- datos inválidos aceptados;
- errores de serialización;
- cambios históricos;
- dependencias externas ocultas;
- puntos donde incorporar un segundo cliente obliga a código específico.

Creá tests para problemas encontrados.

Corregilos.

Repetí.

============================================================ 53. TERCERA PASADA: PENSÁ COMO EL SEGUNDO CLIENTE
============================================================

Después simulá que llega otro cliente con archivos y acuerdos completamente distintos.

Intentá incorporarlo.

Medí mentalmente y, cuando sea posible, concretamente:

¿qué tuve que modificar?

La respuesta ideal:

CONFIGURACIÓN Y MAPPINGS.

Si modificaste core:

justificá si fue:

A. una abstracción general nueva;

o

B. sobreajuste.

Si fue B:

rediseñá.

============================================================ 54. RESULTADO IDEAL DE ESTA SESIÓN
============================================================

Quiero terminar hoy con algo sustancialmente más serio que un script descartable.

No necesariamente un SaaS listo para vender.

Sí quiero el embrión técnicamente correcto del producto.

Idealmente debería poder:

1. tomar archivos ficticios de viajes;
2. tomar liquidaciones ficticias;
3. representar un acuerdo versionado;
4. mapear formatos externos;
5. normalizarlos;
6. relacionar operación con cargos;
7. ejecutar reglas;
8. producir cargos esperados;
9. comparar;
10. clasificar;
11. explicar;
12. preservar provenance;
13. guardar/reproducir auditoría;
14. permitir resolución humana;
15. exportar resultado operativo;
16. producir reporte ejecutivo;
17. correr offline;
18. soportar otro acuerdo radicalmente diferente sin lógica client-specific.

============================================================ 55. CRITERIO DE ÉXITO DEFINITIVO
============================================================

El éxito NO es:

"hicimos una demo linda".

El éxito NO es:

"procesamos un Excel ficticio".

El éxito NO es:

"encontramos tres supuestos errores".

El éxito es dejar construido un núcleo que maximice nuestra capacidad de recibir los primeros datos REALES y aprender rápidamente sin tener que tirar todo y empezar de nuevo.

La pregunta que debe guiar cada decisión es:

¿ESTA DECISIÓN AUMENTA NUESTRA CAPACIDAD DE REPRESENTAR Y AUDITAR DE FORMA CORRECTA, EXPLICABLE Y REUSABLE LOS ACUERDOS REALES QUE TODAVÍA NO CONOCEMOS?

Si sí:

probablemente sea una buena inversión.

============================================================ 56. ENTREGABLE FINAL
============================================================

Al finalizar, entregame un resumen extremadamente concreto con:

1. arquitectura finalmente elegida;
2. stack elegido;
3. por qué elegiste ese stack específicamente para ESTE producto;
4. alternativas importantes que descartaste;
5. qué quedó implementado;
6. qué quedó probado;
7. comandos exactos para ejecutar;
8. cómo abrir/usar la demo;
9. cómo ejecutar una auditoría sin UI;
10. cómo crear un nuevo acuerdo;
11. cómo crear un nuevo mapping;
12. cómo incorporar un segundo cliente;
13. resultados de tests;
14. resultados de benchmarks;
15. bugs encontrados durante revisión adversarial;
16. cómo fueron corregidos;
17. limitaciones conocidas;
18. supuestos comerciales todavía NO validados;
19. supuestos técnicos todavía pendientes;
20. partes que probablemente cambien al ver el primer caso real;
21. qué partes considerás suficientemente generales como para probablemente sobrevivir al primer cliente;
22. qué NO recomendás construir todavía;
23. qué información exacta debemos obtener del primer cliente;
24. cualquier punto donde detectes que estamos accidentalmente construyendo consultoría custom en vez de producto.

Y MUY IMPORTANTE:

NO me digas que el producto está validado.

NO me digas que estas reglas representan cómo funciona el mercado.

NO confundas dataset ficticio con evidencia sectorial.

NO confundas corrección técnica con product-market fit.

Tu misión hoy es otra:

CONSTRUIR LA MEJOR INFRAESTRUCTURA POSIBLE PARA CONVERTIR DATOS, ACUERDOS Y EVIDENCIA REALES DE CLIENTES EN AUDITORÍAS DETERMINISTAS, REPRODUCIBLES, EXPLICABLES Y REUSABLES, MINIMIZANDO TANTO EL RIESGO DE FALSAS CONCLUSIONES COMO EL RIESGO DE TENER QUE REPROGRAMAR EL PRODUCTO PARA CADA NUEVA EMPRESA.

TENÉS AUTONOMÍA TÉCNICA PARA ENCONTRAR EL MEJOR CAMINO.

EMPEZÁ A IMPLEMENTAR.
